import json
from pathlib import Path
from typing import Any

from .utils import clear_globals


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
        """Main construct method.

        Args:
            name (str): A prefix name of final DAG.
            path (str | Path):
            gb (dict[str, Any]): A global variables.
        """
        self.name: str = name
        self.path: Path = Path(path)
        self.gb: dict[str, Any] = clear_globals(gb or globals())
        print(json.dumps(self.gb, default=str, indent=1))

    def gen(self): ...
