import json
import os
from typing import Any


class TweakInfo:
    file_path: str
    featured: bool
    min_ios: str | None
    max_ios: str | None
    version_range: str | None
    source: str | None
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.data = self._load_data()
    
    def _load_data(self) -> None:
        # Load
        if not os.path.isfile(self.file_path):
            data = {}
        else:
            try:
                with open(self.file_path) as info_file:
                    data = json.load(info_file)
            except:
                data = {}
        
        if not isinstance(data, dict):
            raise Exception(f"Data in info json '{self.file_path}' isn't a dict.")
        
        # Set properties
        self.featured = data.get("featured", False)
        self.min_ios = data.get("min_ios")
        self.max_ios = data.get("max_ios")

        if self.min_ios and self.max_ios:
            self.version_range = f"{self.min_ios} to {self.max_ios}"
        elif self.min_ios and not self.max_ios:
            self.version_range = f"{self.min_ios}+"
        elif not self.min_ios and self.max_ios:
            self.version_range = f"Up to {self.max_ios}"
        else:
            self.version_range = "Unknown"
        
        self.source = data.get("source")
    
    def get_info_dict(self) -> dict[str, Any]:
        return {
            "featured": self.featured,
            "min_ios": self.min_ios,
            "max_ios": self.max_ios,
            "version_range": self.version_range,
            "source": self.source
        }