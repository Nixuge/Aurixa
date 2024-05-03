import json
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
        return data

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
    