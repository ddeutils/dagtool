from pathlib import Path
from typing import Any


class DokDag:
    """DokDag object that will use be main interface object for retrieve config
    data from the current path.
    """

    def __init__(
        self,
        name: str,
        path: str | Path,
        gb: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.path = Path(path)
        self.gb = gb or globals()

    def gen(self): ...
