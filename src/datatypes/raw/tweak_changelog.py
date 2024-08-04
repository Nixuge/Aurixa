import json
import logging
import os
from packaging import version
from packaging.version import Version

# Could use some inheritance between this & TweakInfo for the _load_data function but meh
class TweakChangelog:
    file_path: str
    data: list[dict[str, str]]
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.data = self._load_data()
    
    def _load_data(self) -> list[dict[str, str]]:
        if not os.path.isfile(self.file_path):
            data = []
        else:
            try:
                with open(self.file_path) as changelog_file:
                    data = json.load(changelog_file)
            except:
                data = []
        
        if not isinstance(data, list):
            raise Exception(f"Data in changelog json '{self.file_path}' isn't a list.")

        data.reverse()
        self._check_data_order(data)

        return data

    def _check_data_order(self, data: list) -> bool:
        sorted_data = list(data)
        sorted_data.sort(key = lambda x: x["version"], reverse=True)

        for i, elem in enumerate(data): # data & sorted_data same length
            v1 = elem["version"]
            v2 = sorted_data[i]["version"]
            if v1 != v2:
                logging.warn(f"Looks like your changelog isn't ordered properly for file '{self.file_path}' !")
                logging.warn(f"Mismatched version: {v1} (provided)/ {v2} (sorted)")
                logging.warn(f"If this intended, please open an issue as Aurixa doesn't provide an option to disable this for now.")
                logging.warn(f"Do you want to stop the program and fix the error? (Y/n)")
                if input() not in ("n", "no", "non"):
                    logging.info(f"Stopped.")
                    exit(1)
                return True

        return False

    def _save_data(self) -> None:
        with open(self.file_path, "w") as changelog_file:
            json.dump(self.data, changelog_file, indent=4)

    def get_latest_version_changelog(self) -> Version | None:        
        if len(self.data) == 0:
            return None
        
        return version.parse(self.data[0]["version"])

    def add_new_version(self, version: str, changes: str) -> None:
        self.data.append({"version": version, "changes": changes})
        self._save_data()
    