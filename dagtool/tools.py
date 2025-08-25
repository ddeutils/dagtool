import logging
import os
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from airflow.models.dag import DAG
from airflow.templates import NativeEnvironment
from jinja2 import Environment, Template
from pydantic import ValidationError

from .conf import YamlConf
from .models import DagModel, pull_vars


class DagTool:
    """DAG Tool Object that is the main interface for retrieve config data from
    the current path and generate Airflow DAG object to global.

    Warnings:
        It is common for dags not to appear due to the `dag_discovery_safe_mode`
        (https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#dag-discovery-safe-mode)

        > If enabled, Airflow will only scan files containing both DAG and
        > airflow (case-insensitive).

        Add this statement on the top of DagTool factory file.
        >>> # from airflow import DAG

    Attributes:
        name (str): A prefix name that will use for making DAG inside this dir.
        path (Path): A parent path for searching tempalate config files.
    """

    # NOTE: Template fields for DAG parameters that will use on different
    #   stages like `catchup` parameter that should disable when deploy to dev.
    template_fields: Sequence[str] = (
        "start_date",
        "catchup",
        "max_active_runs",
    )

    def __init__(
        self,
        name: str,
        path: str | Path,
        *,
        docs: str | None = None,
        # NOTE: Airflow params.
        template_searchpath: list[str | Path] | None = None,
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
        self.docs: str | None = docs
        self.conf: list[DagModel] = []
        self.yaml_loader = YamlConf(path=self.path)

        # NOTE: Airflow params.
        self.template_searchpath = template_searchpath or []
        self.user_defined_filters = user_defined_filters or {}
        self.user_defined_macros = user_defined_macros or {}

        # NOTE: Define tasks that able map to template.
        self.operators: dict[str, Any] = operators or {}

        # NOTE: Start fetch config data.
        self.refresh_conf()

    @property
    def dag_count(self) -> int:
        """Return number of DAG config data that read from template file."""
        return len(self.conf)

    def refresh_conf(self) -> None:
        """Read config from the path argument and reload to the conf."""
        # NOTE: Reset previous if it exists.
        if self.conf:
            self.conf: list[DagModel] = []

        # NOTE: For loop DAG config that store inside this template path.
        for c in self.yaml_loader.read_conf():
            name: str = c["name"]
            env: Environment = self.get_template_env(
                user_defined_macros={
                    "var": pull_vars(name, self.path, prefix=self.name).get,
                    "env": os.getenv,
                }
            )
            self.render_template(c, env=env)
            try:
                model = DagModel.model_validate(c)
                self.conf.append(model)
            except ValidationError:
                continue

    def render_template(self, data: Any, env: Environment) -> Any:
        """Render template."""
        for key in data:
            if key == "default_args":
                data[key] = self.render_template(data[key], env=env)
                continue

            if key in ("tasks", "raw_data") or key not in self.template_fields:
                continue

            value: Any = data[key]
            data[key] = self._render(value, env=env)
        return data

    def _render(self, value: Any, env: Environment) -> Any:
        """Render Jinja template to value.

        Args:
            value (Any): An any value.
            env (Environment): A Jinja environment object.
        """
        if isinstance(value, str):
            template: Template = env.from_string(value)
            return template.render()

        if value.__class__ is tuple:
            return tuple(self._render(element, env) for element in value)
        elif isinstance(value, tuple):
            return value.__class__(*(self._render(el, env) for el in value))
        elif isinstance(value, list):
            return [self._render(element, env) for element in value]
        elif isinstance(value, dict):
            return {k: self._render(v, env) for k, v in value.items()}
        elif isinstance(value, set):
            return {self._render(element, env) for element in value}

        return value

    def get_template_env(
        self,
        *,
        user_defined_macros: dict[str, Any] | None = None,
        user_defined_filters: dict[str, Any] | None = None,
    ) -> Environment:
        """Return Jinja Template Native Environment object.

        Args:
            user_defined_filters:
            user_defined_macros:
        """
        env: Environment = NativeEnvironment()
        udf_macros: dict[str, Any] = self.user_defined_macros | (
            user_defined_macros or {}
        )
        if udf_macros:
            env.globals.update(udf_macros)
        udf_filters: dict[str, Any] = self.user_defined_filters | (
            user_defined_filters or {}
        )
        if udf_filters:
            env.filters.update(udf_macros)
        return env

    def build(
        self,
        default_args: dict[str, Any] | None = None,
        user_defined_macros: dict[str, Any] | None = None,
    ) -> list[DAG]:
        """Build Airflow DAGs from template files.

        Returns:
            list[DAG]: A list of Airflow DAG object.
        """
        dags: list[DAG] = []
        for i, model in enumerate(self.conf, start=1):
            dag: DAG = model.build(
                prefix=self.name,
                docs=self.docs,
                default_args=default_args,
                user_defined_macros=user_defined_macros,
            )
            logging.info(f"({i}) Building DAG: {dag}")
            dags.append(dag)
        return dags

    def build_airflow_dags_to_globals(
        self,
        gb: dict[str, Any],
        *,
        default_args: dict[str, Any] | None = None,
        user_defined_macros: dict[str, Any] | None = None,
    ) -> None:
        """Build Airflow DAG object and set to the globals for Airflow Dag Processor
        can discover them.

        Warnings:
            This method name should include `airflow` and `dag` value because the
        Airflow DAG processor need these words for soft scan DAG file.

        Args:
            gb (dict[str, Any]): A globals object.
            default_args (dict[str, Any]): An override default args value.
            user_defined_macros:
        """
        for dag in self.build(
            default_args=default_args,
            user_defined_macros=user_defined_macros,
        ):
            gb[dag.dag_id] = dag


class DagTemplate:
    """Template DAG object that will use template DAG file to be the template
    of any DAG instead.

        If the DAG template can move all value to variable. It can make template
    of DAG template for make scale DAG factory.
    """

    def __init__(self, name: str) -> None:
        self.name: str = name
