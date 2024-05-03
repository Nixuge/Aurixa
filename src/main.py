import logging
from utils.logger import load_proper_logger
load_proper_logger(logging.getLogger(), True)

from parsers.parse_all_packages import discover_packages
from datatypes.repo import Repo

repo = Repo(discover_packages()) 

# Could be moved to Repo().__init__() w a flag eg "perform_tweak_updates"
for tweak in repo.tweaks:
    tweak.update_changelog_file()

repo.build_entire_repo()
