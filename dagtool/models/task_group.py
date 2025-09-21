from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Literal, Union

try:
    from airflow.sdk.definitions.taskgroup import TaskGroup as _TaskGroup
except ImportError:
    from airflow.utils.task_group import TaskGroup as _TaskGroup

from pydantic import Discriminator, Field, Tag

from ..tasks import Task
from .task import BaseTaskOrTaskGroup

if TYPE_CHECKING:
    try:
        from airflow.sdk.definitions.dag import DAG
    except ImportError:
        from airflow.models.dag import DAG

    from .build_context import BuildContext


class TaskGroup(BaseTaskOrTaskGroup):
    """Group of Task model that will represent Airflow Task Group object."""

    group: str = Field(description="A task group name.")
    type: Literal["group"] = Field(default="A group type.")
    tooltip: str = Field(
        default="",
        description="A task group tooltip that will display on the UI.",
    )
    tasks: list[TaskOrGroup] = Field(
        default_factory=list,
        description="A list of Any Task model.",
    )

    def build(
        self,
        dag: DAG,
        task_group: _TaskGroup | None = None,
        build_context: BuildContext | None = None,
    ) -> _TaskGroup:
        """Build Airflow Task Group object.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            build_context (BuildContext, default None):
                A Context data that was created from the DAG Generator object.

        Returns:
            TaskGroup: An Airflow TaskGroup instance.
        """
        tg = _TaskGroup(
            group_id=self.group,
            tooltip=self.tooltip,
            prefix_group_id=False,
            add_suffix_on_collision=False,
            parent_group=task_group,
            dag=dag,
        )

        for task in self.tasks:
            task.handle_build(
                dag=dag, task_group=tg, build_context=build_context
            )

        return tg

    @property
    def iden(self) -> str:
        """Return Task Group Identity with it group name."""
        return self.group


def any_task_discriminator(value: Any) -> str | None:
    """Any task discriminator function for AnyTask type that dynamic validates
    with Dag.
    """
    if isinstance(value, dict):
        if "group" in value:
            return "Group"
        elif "task" in value:
            return "Task"
        return None
    if hasattr(value, "group"):
        return "Group"
    elif hasattr(value, "task"):
        return "Task"
    # NOTE: Return None if the discriminator value isn't found
    return None


TaskOrGroup = Annotated[
    Union[
        Annotated[Task, Tag("Task")],
        Annotated[TaskGroup, Tag("Group")],
    ],
    Field(
        discriminator=Discriminator(discriminator=any_task_discriminator),
        description="An any task type that able be task or task group model.",
    ),
    # Archive: Keep for optional discriminator.
    # Discriminator(discriminator=any_task_discriminator)
    #
    # Archive: Keep for optional discriminator.
    # Field(
    #     union_mode="left_to_right",
    #     description="An any task type that able operator task or group task.",
    # ),
]
