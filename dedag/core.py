import json
import logging
from pathlib import Path
from typing import Any

from yaml import safe_load

from .const import VARIABLE_FILENAME
from .utils import clear_globals


class DokDag:
    """DokDag object that will use be main interface object for retrieve config
    data from the current path.

    DAG Processor --> DokDag -- file-change --> refresh --> generated --> update cache
                             -- file-not-change --> return cache
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
        self.conf = []

    def read_conf(self):
        # NOTE: Reset previous if it exists.
        self.conf = []
        for file in self.path.rglob("*"):
            if (
                file.is_file()
                and file.stem != VARIABLE_FILENAME
                and file.suffix in (".yml", ".yaml")
            ):
                data = safe_load(file.open(mode="rt"))
                try:
                    if data.get("type", "NOTSET") != "dag":
                        continue
                except AttributeError:
                    # NOTE: Except case data is not be `dict` type.
                    continue
                self.conf.append(
                    {
                        "filename": file.name,
                        "data": data,
                    }
                )

        if len(self.conf) == 0:
            logging.warning("Read config file from this domain path does not exists")

    def gen(self): ...
