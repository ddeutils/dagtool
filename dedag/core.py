import json
import logging
from pathlib import Path
from typing import Any, Callable

from airflow.models.dag import DAG
from pydantic import ValidationError
from yaml import safe_load

from .const import VARIABLE_FILENAME
from .models import DagModel
from .utils import clear_globals


class DeDag:
    """DeDag object that will use be main interface object for retrieve config
    data from the current path.

    DAG Processor --> DeDag --( file-change )--> refresh --> generated --> update cache
                            --( file-not-change )--> return cache
    """

    def __init__(
        self,
        name: str,
        path: str | Path,
        gb: dict[str, Any] | None = None,
        *,
        on_failure_callback: list[Any] | None = None,
        user_defined_filters: dict[str, Callable] | None = None,
    ) -> None:
        """Main construct method.

        Args:
            name (str): A prefix name of final DAG.
            path (str | Path): A current filepath that can receive with string
                value or Path object.
            gb (dict[str, Any]): A global variables.
        """
        self.name: str = name
        self.path: Path = p.parent if (p := Path(path)).is_file() else p
        self.gb: dict[str, Any] = clear_globals(gb or globals())

        print(json.dumps(self.gb, default=str, indent=1))
        self.docs: str | None = self.extract_docs()
        self.conf: list[DagModel] = []
        self.read_conf()
        self.override_conf: dict[str, Any] = {
            "on_failure_callback": on_failure_callback,
            "user_defined_filters": user_defined_filters,
        }

    @property
    def dag_count(self) -> int:
        return len(self.conf)

    def extract_docs(self):
        if "__doc__" in self.gb:
            return self.gb["__doc__"]
        elif "docs" in self.gb and (
            self.gb["__annotations__"].get("docs") is str
        ):
            return self.gb["docs"]
        return None

    def read_conf(self) -> None:
        """Read config from the path argument and reload to the conf."""
        # NOTE: Reset previous if it exists.
        self.conf: list[DagModel] = []
        for file in self.path.rglob("*"):
            if (
                file.is_file()
                and file.stem != VARIABLE_FILENAME
                and file.suffix in (".yml", ".yaml")
            ):
                data: dict[str, Any] | list[Any] = safe_load(
                    file.open(mode="rt")
                )

                # VALIDATE: Does not support for list of template config.
                if isinstance(data, list):
                    continue

                try:
                    if data.get("type", "NOTSET") != "dag":
                        continue
                    file_stats = file.stat()
                    model = DagModel.model_validate(
                        {
                            "filename": file.name,
                            "parent_dir": file.parent,
                            "created_dt": file_stats.st_ctime,
                            "updated_dt": file_stats.st_mtime,
                            **data,
                        }
                    )
                    logging.info(f"Load DAG: {model.name!r}")
                    self.conf.append(model)
                except AttributeError:
                    # NOTE: Except case data is not be `dict` type.
                    continue
                except ValidationError as e:
                    # NOTE: Raise because model cannot validate with model.
                    logging.error(
                        f"Template data cannot pass to DeDag model:\n{e}"
                    )
                    continue

        if len(self.conf) == 0:
            logging.warning(
                "Read config file from this domain path does not exists"
            )

    def build(self): ...

    def gen(self, default_args: dict[str, Any] | None = None):
        dags: list[DAG] = []
        for i, data in enumerate(self.conf, start=1):
            kwargs: dict[str, Any] = {
                "dag_id": data.name,
                "default_args": default_args or {},
            }
            dag: DAG = DAG(**kwargs)
            logging.info(f"({i}) Building DAG: {dag}")
            dags.append(dag)
        return dags
