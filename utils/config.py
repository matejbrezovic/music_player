import json
from typing import Dict, Any


class Config:
    def __init__(self):
        self.__settings: Dict[str, Any] = {}

    def set_setting(self, key: str, value: Any) -> None:
        self.__settings[key] = value

    def get_setting(self, key: str) -> Any:
        return self.__settings[key] if key in self.__settings else None

    def save(self, file_path: str) -> None:
        with open(file_path, 'w', encoding="utf-8") as f:
            json.dump(self.__settings, f,
                      sort_keys=True,
                      indent='\t',
                      separators=(',', ': '),
                      ensure_ascii=False)

    def load(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r', encoding="utf-8") as f:
            try:
                self.__settings = json.load(f)
                return self.__settings
            except json.decoder.JSONDecodeError:
                return {}
