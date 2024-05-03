import bz2
import json
import logging
import lzma
import os
import random
import shutil
import subprocess
from typing import Callable

import jinja2
from datatypes.static.repo_settings import RepoSettings
from datatypes.tweak import Tweak
from utils.hash import hash_file_all_algorithms
from utils.input import log_input


class Repo:
    bf: str = RepoSettings.build_folder #easier access
    tweaks: list[Tweak]
    featured_tweaks: list[Tweak]
    def __init__(self, tweaks: list[Tweak]) -> None:
        logging.debug("Making new repo object")
        self.tweaks = tweaks
        self.featured_tweaks = self._load_featured_tweaks()
        if not os.path.exists("www"):
            logging.debug("Making www folder")
            os.mkdir("www")
    
    def _load_featured_tweaks(self) -> list[Tweak]:
        featured = []

        for tweak in self.tweaks:
            if tweak.info.featured:
                featured.append(tweak)
        
        # When no featured tweaks are present, add a random one.
        # Could also make it not render the part in the html/sileo-build.json,
        # but rn Silica works like that and I like it.
        if len(featured) == 0:
            featured.append(random.choice(self.tweaks))
        
        return featured

    def build_entire_repo(self):
        if RepoSettings.git_repo:
            self.init_git()
        
        self.setup_folders()
        self.copy_static_files()
        self.build_cname()
        # TODO: Make pages to build a config so people can add more pages if needed,
        # then just use self._build_html(page)
        self.build_html_index()
        self.build_html_404()
        self.build_html_add()
        self.build_sileo_featured()

        for tweak in self.tweaks:
            tweak.build_entire_tweak_in_repo()

        self.build_packages_file()
        self.compress_packages_file()

        self.build_release_file()
        if RepoSettings.enable_gpg:
            self.sign_release_file()
        
        if RepoSettings.git_repo:
            self.prompt_commit()
        
        # TODO: api thing?

    def init_git(self):
        # Note: not sure if there's a better way to do it, basically:
        # - git clone (if not exists) or pull
        # - remove everything except .git
        # then at the end see "self.prompt_commit()"
        if not os.path.exists(f"{self.bf}/.git"):
            if os.path.exists(self.bf):
                shutil.rmtree(self.bf)
            os.system(f"git clone {RepoSettings.git_repo} {self.bf}")
        else:
            os.system(f"cd {self.bf} && git pull")
        
        for file in os.listdir(self.bf):
            if file == ".git": continue
            path = f"{self.bf}/{file}"
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)


    def setup_folders(self):
        # Note: could prolly organize this abit better
        # but it's quite nice how it's done in Silica
        for path in (
            "assets/", # tweak assets (icon, ss, banner)
            "depiction/native/help", # sileo depictions (& help sileo depictions)
            "depiction/web", # webpages (could move to tweaks/ or smth more friendly)
            "web/", # web assets (index .css/.js)
            # deb packages. This is 100% technically better in '/assets/' of the tweak,
            # but it's nice to have an easily browsable directory w all tweaks in it.
            "debs",
            "api", # not required for now tbh.
        ):
            if not os.path.exists(f"{self.bf}/{path}"):
                os.makedirs(f"{self.bf}/{path}")
    
    def copy_static_files(self):
        source_icon = "repo/icon.png" if os.path.exists("repo/icon.png") else "repo/styles/default.png"
        shutil.copyfile(source_icon, f"{self.bf}/CydiaIcon.png")

        for file in ("index.css", "index.js"):
            shutil.copyfile(f"repo/styles/{file}", f"{self.bf}/web/{file}")
        
    def build_cname(self):
        with open(f"{self.bf}/CNAME", "w") as f:
            f.write(RepoSettings.cname)

    def _build_html(self, filename: str):
        environment = jinja2.Environment(loader=jinja2.FileSystemLoader("repo/styles/"))
        template = environment.get_template(f"{filename}.jinja")
        content = template.render(
            repo_name = RepoSettings.name,
            tint_color = RepoSettings.tint,
            repo_desc = RepoSettings.description,
            repo_url = RepoSettings.get_full_domain(),
            featured_tweaks = [t.to_dictionary() for t in self.featured_tweaks],
            tweaks = [t.to_dictionary() for t in self.tweaks],
            aurixa_version = RepoSettings.aurixa_version,
            run_date = RepoSettings.run_date,
        )
        with open(f"{self.bf}/{filename}.html", mode="w") as f:
            f.write(content)

    def build_html_index(self):
       self._build_html("index")
    
    def build_html_404(self):
        self._build_html("404")

    def build_html_add(self):
        self._build_html("add")

    def build_sileo_featured(self):
        banners = []

        for featured_tweak in self.featured_tweaks:
            control = featured_tweak.get_latest_control()
            bundle_id = control.get_property("Package")
            banners.append({
                "package": bundle_id,
                "title": control.get_property("Name"),
                "url": f"{RepoSettings.get_full_domain()}/assets/{bundle_id}/banner.png",
                "hideShadow": "false"
            })
        
        data = {
            "class": "FeaturedBannersView",
            "itemSize": "{263, 148}",
            "itemCornerRadius": 8,
            "banners": banners
        }
        with open(f"{self.bf}/sileo-featured.json", "w") as f:
            json.dump(data, f, indent=4)
        
    def build_packages_file(self):
        final_release_text = ""
        for tweak in self.tweaks:
            for package in tweak.packages:
                additional_control_properties = package.hash_patched_file()
                additional_control_properties["Size"] = str(package.size_patched_file())
                additional_control_properties["Filename"] = f"./debs/{package.deb_name}"

                final_release_text += package.control.to_text(additional_control_properties) + "\n"
        
        with open(f"{RepoSettings.build_folder}/Packages", 'w') as f:
            f.write(final_release_text)
    
    def compress_packages_file(self):
        enabled_compressions: dict[str, Callable] = {
            "xz": lzma.open,
            "bz2": bz2.open
        }

        with open(f"{RepoSettings.build_folder}/Packages", "rb") as f_in:
            packages_content = f_in.read()
            for extension, open_method in enabled_compressions.items():
                with open_method(f"{RepoSettings.build_folder}/Packages.{extension}", "wb") as f_out:
                    f_out.write(packages_content)
    
    def _get_hash_sizes_packages_files(self) -> dict[str, list[tuple[str, int, str]]]:
        # Format is the following:
        # hash_type: [(hash, size, filename)]
        files = ("Packages", "Packages.xz", "Packages.bz2")

        res: dict[str, list[tuple[str, int, str]]] = {}

        for file in files:
            file_path = f"{RepoSettings.build_folder}/{file}"
            hashes = hash_file_all_algorithms(file_path)
            for hash_type, hash_value in hashes.items():
                # Get & make list for current hash if not present
                current_hash_list = res.get(hash_type)
                if not current_hash_list:
                    current_hash_list = []
                    res[hash_type] = current_hash_list
                current_hash_list.append((hash_value, os.path.getsize(file_path), file))

        return res
                
    def build_release_file(self):
        with open( f"{RepoSettings.build_folder}/Release", 'w') as f:
            f.write(RepoSettings.get_release_string(self._get_hash_sizes_packages_files()))
    
    def sign_release_file(self):
        release_file = f"{self.bf}/Release"
        gpg_file = f"{release_file}.gpg"

        if os.path.exists(gpg_file):
            os.remove(gpg_file)
        
        key = "Aurixa MobileAPT Repository"
        subprocess.run(f"gpg -abs -u \"{key}\" -o {gpg_file} {release_file}", shell=True, check=True)
    
    def prompt_commit(self):
        if not "y" in log_input("Do you want to commit the changes to your repo?"):
            return

        commit_message = log_input("Enter your commit message (leave empty for 'Updated repo.'): ").strip()
        if commit_message == "":
            commit_message = "[Aurixa] Updated repo."
        else:
            commit_message = "[Aurixa] " + commit_message
        
        os.system(f"cd {RepoSettings.build_folder} && git add . && git commit -m \"{commit_message}\" && git push")