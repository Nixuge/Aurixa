from __future__ import annotations

from dataclasses import dataclass, field
import logging
import tarfile
from typing import IO, Any, Callable, cast
import arpy

from datatypes.static.repo_settings import RepoSettings

# Used to check for absolutely necessary unreplaceable keys when making a new ControlFile object
ESSENTIAL_CONTROL_KEYS = (
    "Package",
    "Name",
    "Architecture",
    "Version",
    # Below are highly recommended properties but not technically required
    # "Depends",
    # "Description",
    # "Author",
)

# Used to check how to handle keys given in the info.json 
# You either give it:
# A string, in which case it's going to simply replace that key in the control's internal dict
# A handler function, in which case that function can itself modify the control's internal dict however it wants
class ControlKeyMeta:
    control_name_or_special_handler: str | Callable
    def __init__(self, control_name_or_special_handler: str | Callable) -> None:
        self.control_name_or_special_handler = control_name_or_special_handler

    def set_control_property(self, properties: dict[str, str], new_value: Any) -> None:
        if isinstance(self.control_name_or_special_handler, str):
            properties[self.control_name_or_special_handler] = new_value
        else:
            self.control_name_or_special_handler(properties, new_value)


class ValidControlKeysHandlers:
    @staticmethod
    def pre_deps(properties: dict[str, str], new_value: list[str]) -> None:
        properties["Pre-Depends"] = ", ".join(new_value)
    
    @staticmethod
    def works_min(properties: dict[str, str], new_value: list[str]) -> None:
        firmware_str = f"firmware (>= {new_value})"

        prop_deps = properties.get("Depends")
        if prop_deps and prop_deps.strip() != "":
            properties["Depends"] = f"{firmware_str}, {prop_deps}"
        else:
            properties["Depends"] = firmware_str
        
        # TODO: REIMPLEMENT TAGS? (for both this & the works_max?)
        # not really sure that's useful in any way tbh.


CKM = ControlKeyMeta # shorter
VALID_META_KEYS: dict[str, ControlKeyMeta] = {
    "homepage": CKM("HomePage"),
    # "works_min": CKM(ValidControlKeysHandlers.works_min),
    # "works_max": CKM(lambda x: x), # do nothing
    "featured": CKM(lambda x: x) # do nothing either
    # Basically here could do handlers for all control files,
    # but if it's YOUR repo you should handle the control files yourself.
}
# NOTE: THAT WHOLE SYSTEM ABOVE (up to line 23) is kinda bloated, intended it to be possible
# to replace any key w the info.json, but actually not sure that's useful.
# Even the works_min should technically be handled in the control of the tweak instead.
# This also eg causes issues with tweaks that have multiple builds for different iOS versions (works_min & works_max) :/

class ControlFile:
    _properties: dict[str, str]

    def __init__(self, control_properties: dict[str, str]) -> None:
        for key in ESSENTIAL_CONTROL_KEYS:
            if control_properties.get(key) == None:
                logging.error(f"Missing essential control file property '{key}' in provided dictionary:")
                logging.error(control_properties)
                raise Exception("")

        self._properties = dict(control_properties)
        self._add_depiction_and_icon_properties()
    
    # PRIVATE
    def _add_depiction_and_icon_properties(self):
        base_url = f"http://{RepoSettings.cname}"
        package = self.get_property("Package")
        props = {
            "Depiction": f"{base_url}/depiction/web/{package}.html",
            "SileoDepiction": f"{base_url}/depiction/native/{package}.json",
            "ModernDepiction": f"{base_url}/depiction/native/{package}.json",
            "Icon": f"{base_url}/assets/{package}/icon.png",
        }
        for key, val in props.items():
            self.add_property(key, val)


    # PUBLIC
    def add_property(self, key: str, value: str):
        self._properties[key] = value
    def get_property(self, key: str):
        return self._properties.get(key)
    def get_full_dict(self): # kinda dirty, needed to render the html pages
        return dict(self._properties)

    
    def add_meta_properties(self, meta_dict: dict[str, Any]):
        for prop, value in meta_dict.items():
            key_meta = VALID_META_KEYS.get(prop)
            if not key_meta:
                logging.warn(f"Invalid property in the tweak meta: {prop} (set to {value})")
                continue
            key_meta.set_control_property(self._properties, value)


    def to_text(self, additional_properties: dict | None = None) -> str:
        final_text = ""
        for prop, value in self._properties.items():
            final_text += f"{prop}: {value}\n"
        
        if isinstance(additional_properties, dict):
            for prop, value in additional_properties.items():
                final_text += f"{prop}: {value}\n"

        return final_text


    # STATIC PUBLIC
    @classmethod
    def from_text(cls, control_text: str) -> ControlFile:
        # Note: this does NOT support control files with multi line properties (yet)
        # iirc my ios repo archiver does support that, might yoink it from there.
        control_properties = {}
        for line in control_text.split("\n"):
            line = line.strip()

            if line == "": 
                continue

            linesplit = line.split(": ")
            if len(linesplit) != 2:
                logging.warn("Splitted line isn't 2 elements long: " + line)
                continue
            start, end = linesplit
            control_properties[start] = end
            
        return ControlFile(control_properties)

    @classmethod
    def from_deb(cls, full_path: str) -> ControlFile:
        try:
            root_ar = arpy.Archive(full_path)
            root_ar.read_all_headers()
            control_bin = root_ar.archived_files[b'control.tar.gz']
            control_bin = cast(IO[bytes], control_bin) # casts r dirty in python, required for next line otherwise py type complain
            control_tar = tarfile.open(fileobj=control_bin) 
            try:
                control_data = control_tar.extractfile("./control").read().decode() #type: ignore - if None, catch the error anyways.
            except Exception as e:
                logging.error(f"Control file couldn't be read inside of deb {full_path}.")
                raise e
            
            return cls.from_text(control_data)

        except Exception as e:
            logging.error(f"Reading control file from deb failed:")
            raise e