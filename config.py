import json
from typing import Dict, Any


class Config:
    def __init__(self):
        self.settings: Dict[str, Any] = {}

    def add_setting(self, key: str, value: Any) -> None:
        self.settings[key] = value

    def get_setting(self, key: str) -> None:
        return self.settings[key] if key in self.settings else None

    def save(self, file_path: str) -> None:
        with open(file_path, 'w') as f:
            json.dump(self.settings, f)

    def load(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            try:
                self.settings = json.load(f)
            except json.decoder.JSONDecodeError:
                return {}
