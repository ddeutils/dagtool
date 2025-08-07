from pathlib import Path
from typing import Any


class DokDag:
    def __init__(self, name: str, path: str | Path, gb: dict[str, Any] | None = None):
        self.name = name
        self.path = Path(path)
        self.gb = gb or globals()

    def gen(self): ...
