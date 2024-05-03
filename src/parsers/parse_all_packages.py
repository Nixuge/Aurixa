import logging
import os

from datatypes.tweak import Tweak

# Could technically be moved to tweak? (at least the part to find debs)
# but i think it's too much bloat for that class

# Could also bemoved to Repo which could be quite nice.
def discover_packages() -> list[Tweak]:
    if not os.path.isdir("repo/packages"):
        logging.warn("Folder 'packages' either isn't a folder or doesn't exist.")
        return []
    
    all_packages: list[Tweak] = []

    for folder in os.listdir("repo/packages"):
        current_folder = f"repo/packages/{folder}"
        # Check if folder
        if not os.path.isdir(current_folder):
            logging.warn(f"'{folder}' isn't a folder, it shouldn't be inside of 'repo/packages/'")
            continue
        
        # Check if has debs
        found_debs: list[str] = []
        for file in os.listdir(current_folder):
            if os.path.isdir(f"{current_folder}/{file}"): continue

            fsplit = file.split(".")
            if len(fsplit) < 2:
                logging.warn(f"File with no extension shouldn't be there: {file}")
                continue

            if fsplit[-1] == "deb":
                found_debs.append(file)
                continue #don't break to check for eventual invalid files still.
        
        if len(found_debs) == 0:
            logging.warn(f"'{folder}' has no deb in it.")
            continue
        
        all_packages.append(Tweak(folder, found_debs))

    return all_packages