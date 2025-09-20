from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field

from dagtool.models.task import TaskModel
from dagtool.providers.common.operators.debug import DebugOperator
from dagtool.providers.common.operators.error import RaiseOperator

if TYPE_CHECKING:
    from dagtool.models.task import DAG, BaseOperator, BuildContext, TaskGroup


class RaiseTask(TaskModel):
    """Raise Task model."""

    uses: Literal["raise"] = Field(description="A raise task name.")
    message: str | None = Field(default=None)
    skipped: bool = Field(default=False)

    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        build_context: BuildContext | None = None,
    ) -> BaseOperator:
        """Build Airflow Raise Operator object.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            build_context (BuildContext, default None):
                A Context data that was created from the DAG Generator object.
        """
        return RaiseOperator(
            message=self.message,
            skipped=self.skipped,
            dag=dag,
            task_group=task_group,
            **self.task_kwargs(),
        )


class DebugTask(TaskModel):
    """Debug Task model."""

    uses: Literal["debug"] = Field(description="A debug task name.")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="A parameters that want to logging.",
    )

    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        build_context: BuildContext | None = None,
    ) -> BaseOperator:
        """Build Airflow Raise Operator object.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            build_context (BuildContext, default None):
                A Context data that was created from the DAG Generator object.
        """
        return DebugOperator(
            task_group=task_group,
            dag=dag,
            debug=self.params,
            **self.task_kwargs(),
        )
