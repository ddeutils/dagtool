from pathlib import Path
from typing import ClassVar


class CoreConf:
    """Core Config object that use to find and map data from the current path.

    ClassAttributes:
        config_filename (str):
        variable_filename (str):
        assert_dir (str):
    """

    config_filename: ClassVar[str] = "dag"
    variable_filename: ClassVar[str] = "variable"
    assert_dir: ClassVar[str] = "assets"

    def __init__(self, path: Path) -> None:
        self.path: Path = path
