from dataclasses import dataclass, field
import json
import os
from typing import Callable

BAD_INPUT = "BAD_INPUT"
@dataclass
class Option:
    question: str
    key: str
    handler: Callable | None = field(default=None)
    # path: list[str] | None = field(default=None) # too lazy to implement since unused lol
    subpath: str | None = field(default=None)

    def ask_and_set(self, dict_to_set: dict):
        # Handle input w retries if invalid
        res = input(self.question)
        if self.handler != None:
            res = self.handler(res)
            while res == BAD_INPUT:
                res = input(self.question)
            

        # Handle subpathes to 
        dict_to_add_key_on: dict
        if self.subpath:
            if not dict_to_set.get(self.subpath):
                dict_to_set[self.subpath] = {}
            dict_to_add_key_on = dict_to_set[self.subpath]
        else:
            dict_to_add_key_on = dict_to_set
        
        # Final set to dict
        dict_to_add_key_on[self.key] = res



def valid_tint(tint: str) -> str:
    if len(tint) == 0:
        print("Please input something")
        return BAD_INPUT
    if tint[0] != "#":
        print("The first character should be a #")
        return BAD_INPUT
    if len(tint) != 7:
        print("The input should be 7 caracters long.") # yes 4 chars could be valid but meh
        return BAD_INPUT
    
    valid_chars = "0123456789abcdefABCDEF"
    for char in tint[1:]:
        if char not in valid_chars:
            print("Invalid character for hex colour: " + char)
            return BAD_INPUT

    return tint

def none_or_repo(repo: str) -> str | None:
    if repo == "":
        return None
    
    if not repo.endswith(".git"):
        print("Provided url doesn't end with '.git'. Make sure you copy the url under the green 'code' button on your repo.")
        return BAD_INPUT
    
    return repo

def to_bool(input: str) -> bool:
    return "y" in input.lower()

OPTIONS = [
    Option("Please enter your repo's name: ", "repo_name"),
    Option("Please enter your repo's description: ", "description"),
    Option("Please enter the tint you want for your repo (in hexadecimal, eg #FC4C02): ", "tint", valid_tint),
    Option("Will your domain have HTTPS enabled? (y/n): ", "https", to_bool),
    Option("What domain are you going to host the repo on ? (don't include https://, just the domain): ", "cname"),
    Option("Do you want to automatically push the repo to a Git server when run? If yes, provide the url. Otherwise, leave blank. See the README for more detailed info about how to set up: ", "git_repo", none_or_repo),
    Option("Do you want to sign your repository with GPG? : ", "enable_gpg", to_bool),
    Option("What's your maintainer name: ", "name", None, "maintainer"),
    Option("What's your maintainer email: ", "email", None, "maintainer"),
]

def is_setup():
    # Could also use settings.json directly
    return os.path.exists(".setup_done")

def setup():
    print("Aurixa setup")
    
    all_opts = {}
    for opt in OPTIONS:
        opt.ask_and_set(all_opts)
    
    with open('repo/settings.json', 'w') as f:
       json.dump(all_opts, f, indent=4)
    
    open(".setup_done", "w").close()

    print("Done saving settings. You can find & modify them manually in the repo/settings.json file")
    
    if not os.path.isdir("repo/packages"): os.makedirs("repo/packages")

    if all_opts.get("enable_gpg"):
        print("Generating GPG keys")
        gen_gpg()
        print("Done generating GPG keys")

def gen_gpg():
    os.system("gpg --batch --gen-key src/gpg/gpg.batchgen")