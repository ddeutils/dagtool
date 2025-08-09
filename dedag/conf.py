from pathlib import Path
from typing import Any

from yaml import safe_load

from .const import VARIABLE_FILENAME


class YamlConf:
    """Core Config object that use to find and map data from the current path.

    ClassAttributes:
        config_filename (str):
        variable_filename (str):
        assert_dir (str):
    """

    def __init__(self, path: Path) -> None:
        self.path: Path = path

    def variable(self, env: str) -> dict[str, Any]:
        search_files: list[Path] = list(self.path.rglob(f"{VARIABLE_FILENAME}.*"))
        if not search_files:
            return {}
        return safe_load(search_files[0].open(mode="rt")).get(env, {})
