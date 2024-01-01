import json
import os.path

from constants import DEFAULT_CONFIG_PATH


class Config:
    def __init__(self):
        self.__settings: dict[str, ...] = {}

    def set_setting(self, key: str, value: ...) -> None:
        self.__settings[key] = value

    def get_setting(self, key: str, default_val: ... = None) -> ...:
        return self.__settings[key] if key in self.__settings else default_val

    def save(self, file_path: str = DEFAULT_CONFIG_PATH) -> None:
        with open(file_path, 'w', encoding="utf-8") as f:
            json.dump(self.__settings, f,
                      sort_keys=True,
                      indent='\t',
                      separators=(',', ': '),
                      ensure_ascii=False)

    def load(self, file_path: str = DEFAULT_CONFIG_PATH) -> dict[str, ...]:
        if not os.path.exists(os.path.dirname(file_path)):
            os.mkdir(os.path.dirname(file_path))

        if not os.path.exists(file_path):
            open(file_path, 'w')

        with open(file_path, 'r', encoding="utf-8") as f:
            try:
                self.__settings = json.load(f)
                return self.__settings
            except json.decoder.JSONDecodeError:
                return {}
