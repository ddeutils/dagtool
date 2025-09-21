from __future__ import annotations

import json
import os
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, overload

try:
    from airflow.sdk.definitions.dag import DAG
    from airflow.sdk.exceptions import AirflowRuntimeError
except ImportError:
    from airflow.models.dag import DAG

    # NOTE: Mock AirflowRuntimeError with RuntimeError.
    AirflowRuntimeError = RuntimeError

from airflow.configuration import conf as airflow_conf
from pendulum import parse, timezone
from pendulum.parsing.exceptions import ParserError
from pydantic import BaseModel, Field
from pydantic.functional_validators import field_validator

from ..const import AIRFLOW_ENV
from ..utils import AIRFLOW_VERSION, DotDict, set_upstream
from .default_args import DefaultArgs
from .task_group import TaskOrGroup

if TYPE_CHECKING:
    from .build_context import BuildContext


class Dag(BaseModel):
    """Dag Model for validate template config data support DagGenerator object.
    This model will include necessary field for Airflow DAG object and dp
    field for DagGenerator object together.
    """

    id: str = Field(description="A DAG ID.")
    type: Literal["dag"] = Field(description="A type of template config.")
    display_name: str | None = Field(
        default=None,
        description=(
            "A DAG display name that support on Airflow version >= 2.9.0"
        ),
    )
    desc: str | None = Field(default=None, description="A DAG description.")
    docs: str | None = Field(
        default=None,
        description="A DAG document that allow to pass with markdown syntax.",
    )
    params: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "a dictionary of DAG level parameters that are made "
            "accessible in templates, namespaced under `params`. These "
            "params can be overridden at the task level."
        ),
    )
    vars: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Custom Jinja macro variables that will use to prepare compound "
            "variable to specific variable for shorten usage in the template."
        ),
    )
    tasks: list[TaskOrGroup] = Field(
        default_factory=list,
        description="A list of any task, origin task or group task",
    )

    # NOTE: Runtime parameters that extract from YAML loader step.
    filename: str | None = Field(
        default=None,
        description="A filename of the current position.",
    )
    parent_dir: Path | None = Field(
        default=None, description="A parent dir path."
    )
    created_dt: datetime | None = Field(
        default=None, description="A file created datetime."
    )
    updated_dt: datetime | None = Field(
        default=None, description="A file modified datetime."
    )
    raw_data: str | None = Field(
        default=None,
        description="A raw data that load from template config path.",
    )
    raw_data_hash: str | None = Field(
        default=None,
        description="A hashed raw data with SHA256.",
    )

    # NOTE: Airflow DAG parameters.
    owner: str = Field(default="dogdag", description="An owner name.")

    # NOTE: Allow passing Jinja template.
    tags: list[str] = Field(
        default_factory=list,
        description="A list of tags. A tag value allow to pass Jinja template.",
    )
    schedule: str | None = Field(
        default=None,
        description=(
            "Defines the rules according to which DAG runs are scheduled. This "
            "value allow to pass with a Jinja template."
        ),
    )
    start_date: datetime | str | None = Field(
        default=None,
        description=(
            "The timestamp from which the scheduler will attempt to backfill. "
            "This value allow to pass with a Jinja template."
        ),
    )
    end_date: datetime | str | None = Field(
        default=None,
        description=(
            "A date beyond which your DAG won't run, leave to None for "
            "open-ended scheduling. This value allow to pass with a Jinja "
            "template."
        ),
    )
    catchup: bool = Field(
        default=False,
        description=(
            "Perform scheduler catchup (or only run latest)? This value allow "
            "to pass with a Jinja template."
        ),
    )
    max_active_tasks: int = Field(
        default_factory=partial(
            airflow_conf.getint,
            "core",
            "max_active_tasks_per_dag",
        ),
        description="the number of task instances allowed to run concurrently",
    )
    max_active_runs: int = Field(
        default_factory=partial(
            airflow_conf.getint, "core", "max_active_runs_per_dag"
        ),
        description=(
            "maximum number of active DAG runs, beyond this number of DAG "
            "runs in a running state, the scheduler won't create "
            "new active DAG runs "
            "(This field allow to pass a Jinja template)."
        ),
    )

    # NOTE: Other Airflow parameters that do not pass Jinja template before
    #   build a DAG object.
    concurrency: int | None = Field(
        default=None,
        description=(
            "A concurrency value that deprecate when upgrade to Airflow3."
        ),
    )
    is_paused_upon_creation: bool = Field(default=True)
    dagrun_timeout_sec: int | None = Field(
        default=None,
        description="A DagRun timeout in second value.",
    )
    owner_links: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Dict of owners and their links, that will be clickable on the DAGs "
            "view UI. Can be used as an HTTP link (for example the link to "
            "your Slack channel), or a mailto link. e.g: "
            '{"dag_owner": "https://airflow.apache.org/"}'
        ),
    )
    fail_stop: bool = Field(
        default=None,
        description="Fails currently running tasks when task in DAG fails.",
    )
    default_args: DefaultArgs = Field(
        default_factory=DefaultArgs,
        description=(
            "A dictionary of default parameters to be used as constructor "
            "keyword parameters when initialising operators."
        ),
    )

    @field_validator(
        "start_date",
        "end_date",
        mode="before",
        json_schema_input_type=str | datetime | None,
    )
    def __prepare_datetime(cls, data: Any) -> Any:
        """Prepare datetime if it passes with datetime string to
        ``pendulum.Datetime`` object.
        """
        if data and isinstance(data, str):
            try:
                return parse(data).in_tz(timezone("Asia/Bangkok"))
            except ParserError:
                return None
        return data

    @field_validator(
        "max_active_runs",
        "max_active_tasks",
        mode="before",
        json_schema_input_type=int | str,
    )
    def __mark_int_json_schema_type(cls, data: Any) -> Any:
        return data

    @field_validator(
        "catchup",
        mode="before",
        json_schema_input_type=bool | str,
    )
    def __mark_bool_json_schema_type(cls, data: Any) -> Any:
        return data

    @overload
    @classmethod
    def build_json_schema(cls, filepath: Path) -> None: ...

    @overload
    @classmethod
    def build_json_schema(cls, filepath: None) -> dict[str, Any]: ...

    @classmethod
    def build_json_schema(
        cls,
        filepath: Path | None = None,
    ) -> dict[str, Any] | None:
        """Build JSON Schema file for this Dag model.

        Args:
            filepath (Path, default None):
                An output filepath that want to save JSON schema content.
        """
        json_schema: Any = cls.model_json_schema(by_alias=True) | {
            "title": "DagTool",
            "description": "a friendly airflow dag build tool",
            "$schema": "http://json-schema.org/draft-07/schema#",
        }
        if not filepath:
            return json_schema

        with filepath.open(mode="w") as f:
            json.dump(json_schema, f, indent=2)
            f.write("\n")
            return None

    def build_docs(self, docs: str | None = None) -> str:
        """Generated document string that merge between parent docs and template
        docs together.

        Args:
            docs (str, default None): A parent documents that want to add on
                the top of template config docs.

        Returns:
            str: A document markdown string that prepared with parent docs.
        """
        base_docs: str = self.docs.rstrip("\n")

        if docs:
            d: str = docs.rstrip("\n")
            docs: str = f"{d}\n\n{base_docs}"
        else:
            docs: str = base_docs

        # NOTE: Exclude jinja template until upgrade Airflow >= 2.9.3, This
        #   version remove template render on the `doc_md` value.
        if AIRFLOW_VERSION <= [2, 9, 3]:
            raw_data: str = f"{{% raw %}}{self.raw_data}{{% endraw %}}"
        else:
            raw_data: str = self.raw_data

        if docs:
            docs += f"\n\n### YAML Template\n\n````yaml\n{raw_data}\n````"
        else:
            docs: str = f"### YAML Template\n\n````yaml\n{raw_data}\n````"
        return f"{docs}\n> Generated by DAG Tools HASH: `{self.raw_data_hash}`."

    def dag_dynamic_kwargs(
        self, factory_kwargs: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Prepare Airflow DAG parameters that do not use for all Airflow
        version.

        Args:
            factory_kwargs (dict[str, Any]): A factory kwargs that set outside
                Dag model field but need to pass to build Airflow DAG object.

        Notes:
            default_view: This value does not set for Airflow major version more
                than 3.
            orientation: Default value is ``LR``.

        Returns:
            dict[str, Any]: A mapping kwargs parameters that depend on the
                Airflow version.
        """
        kw: dict[str, Any] = {}
        factory_kw: dict[str, Any] = factory_kwargs or {}
        _ = factory_kw

        if AIRFLOW_VERSION >= [2, 9, 0]:
            if self.display_name:
                kw.update({"dag_display_name": self.display_name})

        if AIRFLOW_VERSION < [3, 0, 0]:
            # Reference: The 'DAG.concurrency' attribute is deprecated. Please
            #   use 'DAG.max_active_tasks'.
            if self.concurrency:
                kw.update({"concurrency": self.concurrency})

            if self.tags:
                kw.update({"tags": self.tags})

            # NOTE: Specify DAG default view (grid, graph, duration, gantt,
            #   landing_times), default grid.
            kw.update({"default_view": "graph"})

            # NOTE: Specify DAG orientation in graph view (LR, TB, RL, BT),
            #   default LR
            kw.update({"orientation": "LR"})

            if self.fail_stop is not None:
                kw.update({"fail_stop": self.fail_stop})

        if AIRFLOW_VERSION > [3, 0, 0]:
            # NOTE: The tags parameters change to mutable set instead of list
            if self.tags:
                kw.update({"tags": set(self.tags)})
        return kw

    def build(
        self,
        prefix: str | None,
        variables: dict[str, Any] | None = None,
        *,
        docs: str | None = None,
        default_args: dict[str, Any] | None = None,
        user_defined_macros: dict[str, Any] | None = None,
        user_defined_filters: dict[str, Any] | None = None,
        template_searchpath: list[str] | None = None,
        jinja_environment_kwargs: dict[str, Any] | None = None,
        on_success_callback: list[Any] | Any | None = None,
        on_failure_callback: list[Any] | Any | None = None,
        build_context: BuildContext | None = None,
    ) -> DAG:
        """Build Airflow DAG object from the current model field values that
        passing from template and render via Jinja with variables.

        Args:
            prefix (str | None): A prefix of DAG name.
            variables (dict[str, Any]): A variable mapping data.
            docs (str | None): A document string with Markdown syntax.
            default_args: (dict[str, Any]): An override default arguments to the
                Airflow DAG object.
            user_defined_macros (dict[str, Any]): An extended user defined
                macros in Jinja template.
            user_defined_filters (dict[str, Any]): An extended user defined
                filters in Jinja template.
            template_searchpath (list[str], default None): An extended Jinja
                template search path.
            jinja_environment_kwargs:
            on_success_callback (list[Any] | Any | None):
                A list of callback function or a callback function that want to
                trigger call from Airflow DAG after success event.
            on_failure_callback (list[Any] | Any | None):
                A list of callback function or a callback function that want to
                trigger call from Airflow DAG after failure event.
            build_context (BuildContext): A Factory context data that use on
                task building method.

        Returns:
            DAG: An Airflow DAG object.
        """
        _id: str = f"{prefix}_{self.id}" if prefix else self.id
        macros: dict[str, Callable | str] = {
            "env": AIRFLOW_ENV,
            "envs": os.getenv,
            "vars": DotDict(variables).get,
            # NOTE: Allow to pass None value.
            "dag_id_prefix": prefix,
        }
        dag = DAG(
            dag_id=_id,
            description=self.desc,
            doc_md=self.build_docs(docs),
            schedule=self.schedule,
            start_date=self.start_date,
            end_date=self.end_date,
            catchup=self.catchup,
            max_active_runs=self.max_active_runs,
            max_active_tasks=self.max_active_tasks,
            dagrun_timeout=(
                timedelta(seconds=self.dagrun_timeout_sec)
                if self.dagrun_timeout_sec
                else None
            ),
            default_args=(
                {"owner": self.owner}
                | self.default_args.to_dict()
                | DefaultArgs.model_validate(default_args or {}).to_dict()
            ),
            template_searchpath=(template_searchpath or []),
            # template_undefined=...,
            # sla_miss_callback=...,
            # access_control=...,
            user_defined_macros=macros | (user_defined_macros or {}),
            user_defined_filters=(user_defined_filters or {}),
            is_paused_upon_creation=self.is_paused_upon_creation,
            jinja_environment_kwargs=jinja_environment_kwargs,
            render_template_as_native_obj=True,
            on_success_callback=on_success_callback,
            on_failure_callback=on_failure_callback,
            owner_links=self.owner_links,
            # auto_register=...,
            **self.dag_dynamic_kwargs(factory_kwargs={}),
        )

        # NOTE: Build DAG Tasks mapping before set its upstream.
        for task in self.tasks:
            task.handle_build(dag=dag, build_context=build_context)

        # NOTE: Set upstream for each task.
        set_upstream(build_context["tasks"])

        # NOTE: Set property for DAG object.
        dag.is_dag_auto_generated = True

        return dag
