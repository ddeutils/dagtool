from __future__ import annotations

import json
import logging
import os
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from pydantic import ValidationError

from .const import AIRFLOW_ENV, DAG_ID_KEY
from .loader import ASSET_DIR, YamlConf, pull_vars
from .models.dag import Dag
from .renderer import JinjaRender
from .utils import FILTERS, DotDict, clear_globals

if TYPE_CHECKING:
    try:
        from airflow.sdk.bases.operator import BaseOperator
        from airflow.sdk.definitions.dag import DAG
        from airflow.sdk.definitions.mappedoperator import MappedOperator
    except ImportError:
        from airflow.models.baseoperator import BaseOperator
        from airflow.models.dag import DAG
        from airflow.models.mappedoperator import MappedOperator

    from .models.build_context import BuildContext
    from .models.tool import ToolModel

    Operator = BaseOperator | MappedOperator
    T = TypeVar("T")

logger = logging.getLogger("common.factory")


class Factory:
    """Factory object that is the main interface for retrieve tempalte config
    data from the current path and generate Airflow DAG object.

    Warnings:
        It is common for dags not to appear due to the `dag_discovery_safe_mode`
        (https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#dag-discovery-safe-mode)

        > If enabled, Airflow will only scan files containing both DAG and
        > airflow (case-insensitive).

        Add this statement on the top of the Factory file.
        >>> # NOTE: Add this statement for Airflow DAG Processor.
        >>> # from airflow import DAG

    Examples:
        Create the Custom factory that use standard with your operators.
        >>> from dagtool import Factory
        >>> class CustomFactory(Factory):
        ...     builtin_operators = {
        ...         "some-operator-name": ...,
        ...     }

    Attributes:
        name (str): A prefix name that will use for making DAG inside this dir.
        path (Path): A parent path for searching tempalate config files.
        docs (str, default None): A parent document that use to add before the
            template DAG document.

        template_searchpath (list[str | Path] , default None):
        user_defined_filters (dict[str, Callable] , default None):
        user_defined_macros (dict[str, Callable | str] , default None):
        on_success_callback (list[Any] | Any , default None):
        on_failure_callback (list[Any] | Any , default None):
    """

    # NOTE: Template fields for DAG parameters that will use on different
    #   stages like `catchup` parameter that should disable when deploy to dev.
    template_fields: ClassVar[Sequence[str]] = (
        "schedule",
        "start_date",
        "end_date",
        "catchup",
        "tags",
        "max_active_tasks",
        "max_active_runs",
        "vars",
    )

    # NOTE: Excluded template fields for ignore render a Jinja template if its
    #   key name exist in this sequence.
    template_excluded_fields: ClassVar[Sequence[str]] = (
        "tasks",
        "raw_data",
    )

    template_nested_fields: ClassVar[Sequence[str]] = ("default_args",)

    # NOTE: Builtin class variables for making common Factory by inherit.
    builtin_operators: ClassVar[dict[str, type[Operator]]] = {}
    builtin_tasks: ClassVar[dict[str, type[ToolModel]]] = {}

    def __init__(
        self,
        path: str | Path,
        *,
        name: str | None = None,
        docs: str | None = None,
        operators: dict[str, type[BaseOperator]] | None = None,
        tools: dict[str, type[ToolModel]] | None = None,
        python_callers: dict[str, Callable] | None = None,
        template_searchpath: list[str | Path] | None = None,
        jinja_environment_kwargs: dict[str, Any] | None = None,
        user_defined_filters: dict[str, Callable] | None = None,
        user_defined_macros: dict[str, Callable | str] | None = None,
        on_success_callback: list[Any] | Any | None = None,
        on_failure_callback: list[Any] | Any | None = None,
        only_one_dag: bool = True,
        force_raise: bool = True,
    ) -> None:
        """Main construct method.

        Args:
            path (str | Path): A current filepath that can receive with string
                value or Path object.
            name (str): A prefix name of any DAGs that exists in this path.
            docs (dict[str, Any]): A docs string for this Factory will use to
                be the header of full docs.
            operators (dict[str, type[BaseOperator]]): A mapping of name and
                sub-model of BaseOperator object.
            tools (dict[str, type[ToolModel]]):
            python_callers (dict[str, Callable]): A mapping of name and function
                that want to use with Airflow PythonOperator.
            template_searchpath (list[str | Path]): A list of Jinja template
                search path.
            user_defined_filters (dict[str, Callable]): An user defined Jinja
                template filters that will add to Jinja environment.
            user_defined_macros (dict[str, Callable | str]): An user defined
                Jinja template macros that will add to Jinja environment.
            on_success_callback: An on success event callback object that want
                to use on each DAG that was built from template path.
            on_failure_callback: An on failure event callback object that want
                to use on each DAG that was built from template path.
            only_one_dag (bool): A reading config will raise error if template
                config dag set more than one if this value set to True.
            force_raise (bool): Force raise error if a template config dag failed
                on the validation step.

        Notes:
            After set the Factory attributes, it will load template config data
        from the current path and skip template file if it does not read or
        match with template config rules like include `type=dag`.
        """
        self.path: Path = p.parent if (p := Path(path)).is_file() else p
        self.name: str | None = name
        self.docs: str | None = docs
        self.conf: dict[str, Dag] = {}
        self.only_one_dag: bool = only_one_dag
        self.force_raise: bool = force_raise
        self.yaml_loader = YamlConf(path=self.path)

        # NOTE: Set Extended Airflow params with necessary values.
        self.template_searchpath: list[str] = [
            str(p.absolute()) if isinstance(p, Path) else p
            for p in (template_searchpath or [])
        ] + [str((self.path / ASSET_DIR).absolute())]
        self.jinja_environment_kwargs = jinja_environment_kwargs or {}
        self.user_defined_filters = FILTERS | (user_defined_filters or {})
        self.user_defined_macros = user_defined_macros or {}
        self.on_success_callback = on_success_callback
        self.on_failure_callback = on_failure_callback

        # NOTE: Define tools that able map to template.
        self.operators: dict[str, type[BaseOperator]] = (
            self.builtin_operators | (operators or {})
        )
        self.tools: dict[str, type[ToolModel]] = self.builtin_tasks | (
            tools or {}
        )
        self.python_callers: dict[str, Any] = python_callers or {}

        # NOTE: Fetching config data from template path.
        self.refresh_conf()

    def refresh_conf(self) -> None:
        """Read config from the path argument and reload to the conf.

            This method will render Jinja template to the Dag fields raw
        value that match key with the template_fields before start validate the
        model.
        """
        # NOTE: Reset previous if it exists.
        if self.conf:
            self.conf: dict[str, Dag] = {}

        renderer = JinjaRender(
            template_fields=self.template_fields,
            template_excluded_fields=self.template_excluded_fields,
            template_nested_fields=self.template_nested_fields,
            user_defined_macros={
                "envs": os.getenv,
                "env": AIRFLOW_ENV,
                "dag_id_prefix": self.name,
            }
            | self.user_defined_macros,
            user_defined_filters=self.user_defined_filters,
            jinja_environment_kwargs=self.jinja_environment_kwargs,
        )

        logger.info(f"Start read template from {self.path}")
        # NOTE: For loop DAG config that store inside this template path.
        for c in self.yaml_loader.read_dag_conf(
            pre_validate=False,
            only_one_dag=self.only_one_dag,
        ):
            name: str = c[DAG_ID_KEY]

            # NOTE: Override or add the vars macro to the current Jinja
            #   environment object.
            renderer.set_globals(
                {
                    "vars": DotDict(
                        pull_vars(name, self.path, prefix=self.name)
                    ).get
                },
            )
            renderer.render_template(c)
            try:
                model = Dag.model_validate(c)
                self.conf[name] = model
            except ValidationError as err:
                logger.error(str(err))
                if self.force_raise:
                    raise
                continue

    def set_context(
        self,
        custom_vars: dict[str, Any] | None = None,
        extras: dict[str, Any] | None = None,
    ) -> BuildContext:
        """Set context data that bypass to the build method.

        Args:
            custom_vars (dict[str, Any]): A common variables.
            extras (dict[str, Any]): An extra parameters.

        Returns:
            BuildContext: A building context data from the current factory
                arguments.
        """
        _vars: dict[str, Any] = custom_vars or {}
        _extras: dict[str, Any] = extras or {}
        return {
            "path": self.path,
            "yaml_loader": self.yaml_loader,
            "tasks": {},
            "tools": self.tools,
            "operators": self.operators,
            "python_callers": self.python_callers,
            "vars": _vars,
            "extras": _extras,
        }

    def build(
        self,
        default_args: dict[str, Any] | None = None,
        build_context_extras: dict[str, Any] | None = None,
    ) -> list[DAG]:
        """Build Airflow DAGs from template files.

        Args:
            default_args (dict[str, Any]): A mapping of default arguments that
                want to override on the template config data.
            build_context_extras (dict[str, Any]): A context extras.

        Returns:
            list[DAG]: A list of Airflow DAG object.
        """
        logger.info("Start build DAG from Template config data.")
        dags: list[DAG] = []
        build_context: BuildContext = self.set_context(
            extras=build_context_extras
        )
        for i, (name, model) in enumerate(self.conf.items(), start=1):
            variables: dict[str, Any] = pull_vars(
                name=name, path=self.path, prefix=self.name
            )
            dag: DAG = model.build(
                prefix=self.name,
                variables=variables,
                docs=self.docs,
                default_args=default_args,
                # NOTE: Update the model `vars` to the Jinja environment global.
                user_defined_macros=self.user_defined_macros | model.vars,
                user_defined_filters=self.user_defined_filters,
                template_searchpath=self.template_searchpath,
                jinja_environment_kwargs=self.jinja_environment_kwargs,
                on_success_callback=self.on_success_callback,
                on_failure_callback=self.on_failure_callback,
                # NOTE:
                #   - Copy the building context data and add the current
                #     custom vars.
                #   - Reset tasks mapping.
                build_context=build_context | {"vars": model.vars, "tasks": {}},
            )
            logger.info(f"({i}) Building DAG: {name}")
            dags.append(dag)
        return dags

    def build_airflow_dags_to_globals(
        self,
        gb: dict[str, Any],
        *,
        default_args: dict[str, Any] | None = None,
        build_context_extras: dict[str, Any] | None = None,
    ) -> None:
        """Build Airflow DAG object and set to the globals for Airflow Dag Processor
        can discover them.

        Warnings:
            This method name should include `airflow` and `dag` value because the
        Airflow DAG processor need these words for soft scan DAG file.

        Args:
            gb (dict[str, Any]): A globals object.
            default_args (dict[str, Any]): An override default args value.
            build_context_extras (dict[str, Any]): A context extras.
        """
        if gb:
            logger.debug("DEBUG: The current globals variables before build.")
            logger.debug(json.dumps(clear_globals(gb), default=str, indent=1))

        for dag in self.build(
            default_args=default_args,
            build_context_extras=build_context_extras,
        ):
            gb[dag.dag_id] = dag
