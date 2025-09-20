from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeAlias, Union

try:
    from airflow.sdk.bases.operator import BaseOperator
    from airflow.sdk.definitions.dag import DAG
    from airflow.sdk.definitions.taskgroup import TaskGroup
except ImportError:
    from airflow.models.baseoperator import BaseOperator
    from airflow.models.dag import DAG
    from airflow.utils.task_group import TaskGroup

from pydantic import BaseModel

if TYPE_CHECKING:
    from dagtool.models.build_context import BuildContext

__all__: tuple[str, ...] = (
    "ToolMixin",
    "ToolModel",
    "DAG",
    "TaskGroup",
    "BaseOperator",
)

OperatorOrTaskGroup: TypeAlias = Union[BaseOperator, TaskGroup]


class ToolMixin(ABC):
    """Tool Mixin Abstract class override the build method."""

    @abstractmethod
    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        build_context: BuildContext | None = None,
    ) -> OperatorOrTaskGroup:
        """Tool building method for build any Airflow task object. This method
        can return Operator or TaskGroup object.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            build_context (BuildContext, default None):
                A Context data that was created from the DAG Generator object.

        Returns:
            Operator | TaskGroup: This method can return depend on building
                logic that already pass the DAG instance from the parent.
        """
        raise NotImplementedError(
            "This Tool object should implement build method."
        )


class ToolModel(BaseModel, ToolMixin, ABC):
    """Tool Model.

    This model will use to be the abstract model for any Tool model that it want
    to use with a specific use case like CustomTask, etc.
    """
