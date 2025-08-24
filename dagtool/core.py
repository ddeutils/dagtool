import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from airflow.models.dag import DAG

from .conf import YamlConf
from .models import DagModel


class DagTool:
    """DAG Tool Object that is the main interface for retrieve config data from
    the current path and generate Airflow DAG object to global.

    DAG Processor --> DagTool --( file-change )--> refresh --> generated --> update cache
                            --( file-not-change )--> return cache
    """

    def __init__(
        self,
        name: str,
        path: str | Path,
        docs: str | None = None,
        *,
        # NOTE: Airflow params.
        on_failure_callback: list[Any] | None = None,
        user_defined_filters: dict[str, Callable] | None = None,
        user_defined_macros: dict[str, Any] | None = None,
        # NOTE: DagTool params.
        operators: dict[str, Any] | None = None,
    ) -> None:
        """Main construct method.

        Args:
            name (str): A prefix name of final DAG.
            path (str | Path): A current filepath that can receive with string
                value or Path object.
            docs (dict[str, Any]): A docs string for this DagTool will use to
                be the header of full docs.
        """
        self.name: str = name
        self.path: Path = p.parent if (p := Path(path)).is_file() else p
        # self.gb: dict[str, Any] = clear_globals(gb or globals())
        # print(json.dumps(self.gb, default=str, indent=1))
        # self.docs: str | None = self.extract_docs()
        self.docs: str | None = docs
        self.conf: list[DagModel] = []
        self.yaml_loader = YamlConf(path=self.path)
        self.refresh_conf()
        self.override_conf: dict[str, Any] = {
            "on_failure_callback": on_failure_callback,
            "user_defined_filters": user_defined_filters,
            "user_defined_macros": user_defined_macros,
        }

        # NOTE: Define tasks that able map to template.
        self.operators: dict[str, Any] = operators or {}

    @property
    def dag_count(self) -> int:
        return len(self.conf)

    def refresh_conf(self) -> None:
        """Read config from the path argument and reload to the conf."""
        # NOTE: Reset previous if it exists.
        if self.conf:
            self.conf: list[DagModel] = []

        self.conf: list[DagModel] = self.yaml_loader.read_conf()

    def gen(self, default_args: dict[str, Any] | None = None) -> list[DAG]:
        """Generated DAGs."""
        dags: list[DAG] = []
        for i, data in enumerate(self.conf, start=1):
            kwargs: dict[str, Any] = {
                "dag_id": f"{self.name}_{data.name}",
                "default_args": default_args or {},
                "template_searchpath": [self.path / "assets"],
            }
            dag: DAG = DAG(**kwargs)
            logging.info(f"({i}) Building DAG: {dag}")
            dags.append(dag)
        return dags

    def build_to_globals(
        self,
        gb: dict[str, Any],
        default_args: dict[str, Any] | None = None,
    ) -> None:
        """Build Airflow DAG object and set to the globals for Airflow Dag Processor
        can discover them.

        Args:
            gb (dict[str, Any]):
            default_args (dict[str, Any]): An override default args value.
        """
        for dag in self.gen(default_args=default_args):
            gb[dag.dag_id] = dag


class DagTemplate:
    """Template DAG object that will use template DAG file to be the template
    of any DAG instead.

        If the DAG template can move all value to variable. It can make template
    of DAG template for make scale DAG factory.
    """

    def __init__(self, name: str) -> None:
        self.name: str = name
