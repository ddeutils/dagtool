from __future__ import annotations

from abc import ABC, abstractmethod
from functools import partial
from typing import TYPE_CHECKING, Any, Literal, TypeAlias, Union

try:
    from airflow.sdk.bases.operator import BaseOperator
    from airflow.sdk.definitions.dag import DAG
    from airflow.sdk.definitions.mappedoperator import MappedOperator
    from airflow.sdk.definitions.taskgroup import TaskGroup
except ImportError:
    from airflow.models.baseoperator import BaseOperator
    from airflow.models.dag import DAG
    from airflow.models.mappedoperator import MappedOperator
    from airflow.utils.task_group import TaskGroup

from airflow.configuration import conf as airflow_conf
from airflow.utils.trigger_rule import TriggerRule
from pydantic import ConfigDict, Field
from pydantic.functional_validators import field_validator

from ..utils import get_id
from .datahub import Dataset
from .tool import ToolModel

if TYPE_CHECKING:
    from .build_context import BuildContext

Operator = BaseOperator | MappedOperator
OperatorOrTaskGroup: TypeAlias = Union[Operator, TaskGroup]


class BaseTaskOrTaskGroup(ToolModel, ABC):
    """Base Task model that represent Airflow Task object."""

    desc: str | None = Field(
        default=None,
        description=(
            "A Airflow task description that will pass to the `doc` argument."
        ),
    )
    upstream: list[str] = Field(
        default_factory=list,
        validate_default=True,
        description=(
            "A list of upstream task name or only task name of this task."
        ),
    )

    @field_validator(
        "upstream",
        mode="before",
        json_schema_input_type=str | list[str] | None,
    )
    def __prepare_upstream(cls, data: Any) -> Any:
        """Prepare upstream value that passing to validate with string value
        instead of list of string. This function will create list of this value.

        Args:
            data (Any): An any upstream data that pass before validating.
        """
        if data is None:
            return []
        elif data and isinstance(data, str):
            return [data]
        return data

    def handle_build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        build_context: BuildContext | None = None,
    ) -> OperatorOrTaskGroup:
        """Handle building method.

        This method will update tasks building context value before returning
        result from building.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            build_context (BuildContext, default None):
                A Context data that was created from the DAG Factory object.
        """

        rs: OperatorOrTaskGroup = self.build(
            dag=dag,
            task_group=task_group,
            build_context=build_context,
        )

        # NOTE: Update task context.
        if build_context is not None:
            tasks: dict[str, Any] = build_context.get("tasks", {})

            # NOTE:
            #   Support duplicate ID that will use mapping upstream if the
            #   result be task in the task group object that allow ``prefix_group_id``
            #   or ``add_suffix_on_collision`` parameters.
            _id: str = get_id(rs)
            if _id in tasks:
                raise NotImplementedError(
                    f"Task ID was duplicate: {_id}. This template should "
                    f"not allow to set the same ID because it force disable "
                    f"``prefix_group_id`` and ``add_suffix_on_collision``."
                )

            tasks[_id] = {"upstream": self.upstream, "task": rs}

        return rs


class TaskModel(BaseTaskOrTaskGroup, ABC):
    """Task Model.

    This model will add necessary field that use with the Airflow BaseOperator
    object.
    """

    model_config = ConfigDict(use_enum_values=True)

    task: str = Field(description="A task name.")
    type: Literal["task"] = Field(default="task", description="A task type.")
    uses: str = Field(description="A tool type name.")
    trigger_rule: TriggerRule = Field(
        default=TriggerRule.ALL_SUCCESS,
        description=(
            "Task trigger rule. Read more detail, "
            "https://www.astronomer.io/blog/understanding-airflow-trigger-rules-comprehensive-visual-guide/"
        ),
    )
    owner: str | None = Field(default=None, description="An owner name.")
    email: str | list[str] | None = Field(
        default=None,
        description=(
            "the 'to' email address(es) used in email alerts. This can be a "
            "single email or multiple ones. Multiple addresses can be "
            "specified as a comma or semicolon separated string or by passing "
            "a list of strings."
        ),
    )
    email_on_failure: bool = Field(
        default_factory=partial(
            airflow_conf.getboolean,
            "email",
            "default_email_on_failure",
            fallback=True,
        ),
        description=(
            "Indicates whether email alerts should be sent when a task failed"
        ),
    )
    email_on_retry: bool = Field(
        default_factory=partial(
            airflow_conf.getboolean,
            "email",
            "default_email_on_retry",
            fallback=True,
        ),
    )
    depends_on_past: bool = Field(default=False)
    pool: str | None = Field(
        default=None,
        description=(
            "the slot pool this task should run in, slot pools are a "
            "way to limit concurrency for certain tasks."
        ),
    )
    pool_slots: int | None = Field(
        default=None,
        description=(
            "the number of pool slots this task should use (>= 1) "
            "Values less than 1 are not allowed."
        ),
    )
    retries: int | None = Field(default=None, description="A retry count.")
    retry_delay: dict[str, int] | None = Field(default=None)
    retry_exponential_backoff: bool = Field(default=False)
    executor_config: dict[str, Any] | None = Field(default=None)
    inlets: list[Dataset] = Field(
        default_factory=list,
        description="A list of inlets or inlet value.",
    )
    outlets: list[Dataset] = Field(
        default_factory=list,
        description="A list of outlets or outlet value.",
    )

    @abstractmethod
    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        build_context: BuildContext | None = None,
    ) -> OperatorOrTaskGroup:
        """Build the Airflow Operator or TaskGroup object from this model
        field.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            build_context (BuildContext, default None):
                A Context data that was created from the DAG Factory object.
        """

    @property
    def iden(self) -> str:
        """Return the task field value for represent task_id in Airflow Task
        Instance.
        """
        return self.task

    def task_kwargs(self, excluded: list[str] | None = None) -> dict[str, Any]:
        """Prepare the Airflow BaseOperator kwargs from BaseTask fields.

            This method will make key when any field was pass to model and do
        avoid if it is None or default value.

        Notes:
            For the inlets and outlets fields, it will abstract these fields with
        custom Pydantic model. So, they need to use build method before passing
        to the task kwargs.

        Args:
            excluded (list[str], default None):
                An exclude key of task parameters that already mapping from this
                model.
        """
        kws: dict[str, Any] = {
            "task_id": self.iden,
            "trigger_rule": self.trigger_rule,
            "retry_exponential_backoff": self.retry_exponential_backoff,
        }
        if self.desc:
            kws.update({"doc": self.desc})

        # NOTE: Start set Dataset for ``inlets`` and ``outlets`` fields.
        if self.inlets:
            inlets: list[Any] = []
            for inlet in self.inlets:
                try:
                    inlets.append(inlet.build())
                except ImportError:
                    continue
            kws.update({"inlets": inlets})
        if self.outlets:
            outlets: list[Any] = []
            for outlet in self.inlets:
                try:
                    outlets.append(outlet.build())
                except ImportError:
                    continue
            kws.update({"outlets": outlets})
        if self.executor_config:
            kws.update({"executor_config": self.executor_config})
        if self.retries:
            kws.update({"retries": self.retries})
        if self.retry_delay:
            kws.update({"retry_delay": self.retry_delay})
        if self.owner:
            kws.update({"owner": self.owner})
        if self.pool:
            kws.update({"pill": self.pool})
        if self.pool_slots:
            kws.update({"pool_slots": self.pool_slots})

        # NOTE: Remove exclude keys.
        for key in excluded or []:
            if key in kws:
                kws.pop(key)

        return kws
