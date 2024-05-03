import json
import logging
import os
import shutil
from typing import cast
import jinja2
import mistune
from packaging import version
from packaging.version import Version
from datatypes.raw.tweak_changelog import TweakChangelog
from datatypes.package import Package
from datatypes.raw.tweak_info import TweakInfo
from datatypes.static.repo_settings import RepoSettings
from utils.input import blank_log_input, log_input
from utils.screenshots import get_screenshot_size


class Tweak:
    """
    Represents a single tweak which can have multiple versions (packages) in it.
    """
    folder_name: str
    packages: list[Package]
    meta_folder: str
    changelog: TweakChangelog
    info: TweakInfo
    screenshots: list[str]

    def __init__(self, folder_name: str, debs: list[str], do_setup_if_required: bool = True) -> None:
        logging.debug(f"Loading tweak {folder_name}")
        self.folder_name = folder_name

        packages_unsorted = [Package(folder_name, deb) for deb in debs]
        self.packages = sorted(packages_unsorted, key=lambda package: package.version, reverse=True) #reverse for descending order

        self.meta_folder = f"repo/packages/{self.folder_name}/meta"

        if do_setup_if_required and not self.is_setup():
            self.setup()

        self.changelog = TweakChangelog(f"{self.meta_folder}/changelog.json")
        self.info = TweakInfo(f"{self.meta_folder}/info.json")

        self.screenshots = []
        if os.path.isdir(f"{self.meta_folder}/screenshots/"):
            for file in os.listdir(f"{self.meta_folder}/screenshots/"):
                self.screenshots.append(file)
            self.screenshots.sort()

    def get_latest_control(self):
        return self.packages[0].control

    def add_meta_properties_to_control(self):
        pass #TODO ?
        # this is supposedly here to eg add "Homepage" to the control file,
        # or eventually to replace any other property.
        # Problem is: i don't think this is really useful if you control (lol) the control file
        # yourself.
        # For now leaving the code in the ControlFile tab, might be useful if you want to make
        # a repo where you don't have access to the tweak build yourself (eg a rehost).
    
    # INFO META
    # SETUP
    def is_setup(self) -> bool:
        for path in (self.meta_folder, f"{self.meta_folder}/info.json", f"{self.meta_folder}/changelog.json", f"{self.meta_folder}/description.md"):
            if not os.path.exists(path):
                return False
        return True

    def setup(self) -> None:
        # Not even sure if adding a "homepage" thing is useful here :/
        data = {
            "featured": "y" in log_input("Should the package be featured? (y/n): ").lower(),
            "source": blank_log_input("Is your package open source? If so, enter the url leave (otherwise leave empty): "),
            "min_ios": blank_log_input("Enter the lowest iOS version your package is compatible with (can be blank): "),
            "max_ios": blank_log_input("Enter the highest iOS version your package is compatible with (can be blank): ")
        }
        if not os.path.exists(self.meta_folder):
            os.makedirs(self.meta_folder)
        
        with open(f"{self.meta_folder}/info.json", "w") as info_file:
            json.dump(data, info_file, indent=4)
        
        with open(f"{self.meta_folder}/changelog.json", "w") as changelog_file:
            changelog_file.write("[]")
        
        with open(f"{self.meta_folder}/description.md", "w") as description_file:
            description_file.write(f"# {self.get_latest_control().get_property("Name")}\n\nYour description here")

        if not os.path.exists(f"{self.meta_folder}/screenshots"):
            os.makedirs(f"{self.meta_folder}/screenshots")

        logging.info(f"Setup for {self.folder_name} done.")
        logging.info("you can now write your description 'meta/description.md'")
        logging.info("and place your icon/banner as 'meta/icon.png' & 'meta/banner.png'")
        logging.info("If you want to include screenshots, place them under 'meta/screenshots/'. Their order is alphabetical (0-9 then a-z)")

    # READ
    def get_info_meta(self):
        pass

    def to_dictionary(self):
        return {
            "control": self.get_latest_control().get_full_dict(),
            "info": self.info.get_info_dict(),
            "changelog": self.changelog.data,
            "screenshots": self.screenshots
        }

    # CHANGELOG
    # Could add the below to init
    def _get_latest_deb_version(self) -> Version:
        versions_str = [cast(str, pkg.control.get_property("Version")) for pkg in self.packages]
        versions: list[Version] = []
        for ver in versions_str:
            versions.append(version.parse(ver))
        
        return max(versions)

    def update_changelog_file(self) -> None:
        latest_version = self._get_latest_deb_version()
        latest_reported_version = self.changelog.get_latest_version_changelog()

        if not latest_reported_version or latest_reported_version < latest_version:
            logging.info(f"Please input your changelog changes for version {latest_version}:")
            changelog_info = input()
            self.changelog.add_new_version(str(latest_version), changelog_info)

    # BUILDING
    def build_entire_tweak_in_repo(self):
        for package in self.packages:
            package.patch_copy_deb_file()
        
        self.build_native_depiction()
        self.build_native_help_depiction()
        self.build_web_depiction()
        self.copy_assets()
        # TODO: help for native depiction in depiction/native/help

    def build_native_depiction(self):
        control = self.get_latest_control()

        main_views = []

        # Screenshot carousel (if any)
        if len(self.screenshots) > 0:
            main_views.append({
                "class": "DepictionScreenshotsView",
                "screenshots": [{"accessibilityText": "Screenshot", "url": f"{RepoSettings.get_full_domain()}/assets/{control.get_property("Package")}/screenshots/{image}"} for image in self.screenshots],
                "itemCornerRadius": 8,
                "itemSize": get_screenshot_size(f"repo/packages/{self.folder_name}/meta/screenshots/")
            })

        # Body
        with open(f"{self.meta_folder}/description.md") as f:
            markdown = f.read()
        main_views.append({
            "markdown": markdown,
            "useSpacing": "true",
            "class": "DepictionMarkdownView"
        })

        # Start of "info" footer
        main_views += [
            {
                "class": "DepictionSpacerView"
            },
            {
                "class": "DepictionHeaderView",
                "title": "Information",
            },
            {
                "class": "DepictionTableTextView",
                "title": "Developer",
                "text": control.get_property("Author")
            },
            {
                "class": "DepictionTableTextView",
                "title": "Version",
                "text": control.get_property("Version")
            }
        ]

        # Compatibility (only if version_range is set in config)
        if self.info.version_range:
            main_views.append({
                "class": "DepictionTableTextView",
                "title": "Compatibility",
                "text": "iOS " + self.info.version_range
            })

        # Rest of "info" footer
        main_views += [
            {
                "class": "DepictionTableTextView",
                "title": "Section",
                "text": control.get_property("Section")
            },
            {
                "class": "DepictionSpacerView"
            }
        ]
        
        # Unsure as to how I should display that 
        # but this color looks pretty nice like that
        if self.info.source:
            main_views.append({
                "class": "DepictionTableButtonView",
                "title": "Source code",
                "action": self.info.source,
                "openExternal": "true",
                "tintColor": "#aaaaaa"
            })

        # TODO: ADD THIS PAGE & RE ENABLE THIS
        # main_views.append({
        #     "class": "DepictionTableButtonView",
        #     "title": "Contact Support",
        #     "action": f"depiction-{RepoSettings.get_full_domain()}/depiction/native/help/{control.get_property("Package")}.json",
        #     "openExternal": "true",
        #     "tintColor": RepoSettings.tint
        # })

        footer = {
            "class": "DepictionLabelView",
            "text": f"Aurixa {RepoSettings.aurixa_version} - Updated {RepoSettings.run_date}",
            "textColor": "#999999",
            "fontSize": "10.0",
            "alignment": 1
        }

        main_views.append(footer)

        depiction = {
            "minVersion": "0.1",
            "headerImage": f"{RepoSettings.get_full_domain()}/assets/{control.get_property("Package")}/banner.png",
            "tintColor": RepoSettings.tint,
            "tabs": [
                {
                    "tabname": "Details",
                    "views": main_views,
                    "class": "DepictionStackView"
                },
                {
                    "tabname": "Changelog",
                    # Note: if packages don't have a changelog, there's an issue somewhere, so no "This package has no changelog." failsafe unlike in Silica
                    "views": [{"class": "DepictionMarkdownView", "markdown": f"#### Version {entry['version']}\n\n{entry['changes']}"} for entry in self.changelog.data]+[footer],
                    "class": "DepictionStackView"
                }
            ],
            "class": "DepictionTabView"
        }

        with open(f"{RepoSettings.build_folder}/depiction/native/{control.get_property("Package")}.json", "w") as f:
            json.dump(depiction, f, separators=(',', ':'), indent=4)
    
    def build_native_help_depiction(self):
        logging.warn("TODO: build_native_help_depiction")
    
    def build_web_depiction(self):
        environment = jinja2.Environment(loader=jinja2.FileSystemLoader("repo/styles/"))
        template = environment.get_template("tweak.jinja")

        with open(f"{self.meta_folder}/description.md") as f:
            markdown = mistune.markdown(f.read())

        content = template.render(
            tint_color = RepoSettings.tint,
            repo_url = RepoSettings.cname,
            tweak = self.to_dictionary(),
            full_description = markdown,
            aurixa_version = RepoSettings.aurixa_version,
            run_date = RepoSettings.run_date,
        )

        with open(f"{RepoSettings.build_folder}/depiction/web/{self.get_latest_control().get_property("Package")}.html", mode="w") as f:
            f.write(content)
    
    def copy_assets(self):
        result_folder = f"{RepoSettings.build_folder}/assets/{self.get_latest_control().get_property("Package")}"
        if not os.path.exists(f"{result_folder}/screenshots"):
            os.makedirs(f"{result_folder}/screenshots")
        
        meta_folder = f"repo/packages/{self.folder_name}/meta"
        fallback_folder = f"repo/styles/default_tweak_assets"

        # Copy png files
        for file in ("banner.png", "icon.png"):
            source_path = f"{meta_folder}/{file}"
            if not os.path.exists(source_path):
                source_path = f"{fallback_folder}/{file}"
            shutil.copy(source_path, f"{result_folder}/{file}")
        
        # Copy description (no fallback as there should always be one)
        shutil.copy(f"{meta_folder}/description.md", f"{result_folder}/description.md")

        # Clear old & copy new screenshots
        if os.path.exists(f"{result_folder}/screenshots"):
            shutil.rmtree(f"{result_folder}/screenshots")
        
        if os.path.exists(f"{meta_folder}/screenshots"):
            shutil.copytree(f"{meta_folder}/screenshots", f"{result_folder}/screenshots")
