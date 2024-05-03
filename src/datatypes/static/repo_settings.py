from __future__ import annotations
from datetime import datetime

import pyjson5

class RepoSettings:
    """
    Represents the settings for your repo.
    """
    name: str
    description: str
    tint: str
    https: bool
    cname: str
    auto_git: bool
    maintainer_name: str
    maintainer_email: str
    build_folder: str
    run_date: str
    aurixa_version: str = "1.0" # TODO: MOVE
    
    @classmethod
    def _init(cls, json_path: str) -> None:
        with open(json_path) as f:
            data = pyjson5.loads(f.read())
        
        cls.name = data.get("repo_name")
        cls.description = data.get("description")
        cls.tint = data.get("tint")
        cls.https = data.get("https")
        cls.cname = data.get("cname")

        cls.auto_git = data.get("auto_git", False)

        maintainer_part = data.get("maintainer")
        cls.maintainer_name = maintainer_part.get("name")
        cls.maintainer_email = maintainer_part.get("email")

        cls.build_folder = data.get("build_folder", "www")
        cls.run_date = datetime.now().strftime("%Y-%m-%d")
    
    @classmethod
    def get_full_domain(cls):
        prefix = "https" if cls.https else "http"
        return f"{prefix}://{cls.cname}"

    @classmethod
    def get_release_string(cls, hashes_sizes: dict[str, list[tuple[str, int, str]]]):
        props = {
            "Origin": cls.name,
            "Label": cls.name,
            "Suite": "stable",
            "Version": "1.0", # TODO: allow changing this
            "Codename": "ios", #same
            "Architectures": "iphoneos-arm iphoneos-arm64", # this too (loop over all controls to check if any doesnt have an arch?)
            "Components": "main", # same
            "Description": cls.description
        }

        release_str = ""
        for key, value in props.items():
            release_str += f"{key}: {value}\n"
        release_str += "\n"

        # Format:
        # HASH:
        #  <hash> <size in bytes> <filename>
        for hash_type, hashes_data in hashes_sizes.items():
            release_str += f"{hash_type}:\n"
            for hash_data in hashes_data:
                release_str += f" {hash_data[0]} {hash_data[1]} {hash_data[2]}\n"
            release_str += "\n"
        
        return release_str

RepoSettings._init("repo/settings.json")