import hashlib
import io
import logging
import os
import random
import shutil
import subprocess
import tarfile
from typing import Callable, cast

from datatypes.raw.control_file import ControlFile
from packaging import version
from packaging.version import Version

from datatypes.static.repo_settings import RepoSettings
from utils.hash import hash_file_all_algorithms

class Package:
    """
    Represents a package for a tweak.
    """
    deb_name: str
    initial_path: str
    final_path: str
    control: ControlFile
    version: Version
    def __init__(self, folder_name: str, deb_name: str) -> None:
        logging.debug(f"Loading deb {deb_name} for {folder_name}")
        self.deb_name = deb_name
        self.initial_path = f"repo/packages/{folder_name}/{deb_name}"
        self.final_path = f"{RepoSettings.build_folder}/debs/{self.deb_name}"

        self.control = ControlFile.from_deb(self.initial_path)
        self.version = version.parse(cast(str, self.control.get_property("Version")))
    
    def patch_copy_deb_file(self):
        # NOTE: THIS IS LINUX ONLY FOR NOW!
        # ALSO, IF POSSIBLE, FIND A WAY TO EDIT ARCHIVES ON THE FLY & NOT RECOMPRESS.
        # neither arpy or unix_ar seem to support it unfortunately so for now sticking w good old shell
        tmpfolder = f"tmp/{random.randint(1000000, 10000000)}"
        os.makedirs(tmpfolder)

        # extract
        subprocess.run(f"dpkg-deb -R {self.initial_path} {tmpfolder}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        # edit control
        with open(f"{tmpfolder}/DEBIAN/control", "w") as f:
            f.write(self.control.to_text())
        # re package
        subprocess.run(f"dpkg-deb -b {tmpfolder} {self.final_path}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        shutil.rmtree(tmpfolder)
    
    def hash_patched_file(self) -> dict[str, str]:
        return hash_file_all_algorithms(self.final_path)

    def size_patched_file(self) -> int:
        return os.path.getsize(f"{self.final_path}")