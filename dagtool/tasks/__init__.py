from typing import Annotated, Any, Union

from airflow.models import DAG, Operator
from airflow.utils.task_group import TaskGroup
from pydantic import Field

from dagtool.utils import TaskMapped, set_upstream

from .__abc import BaseTask, BaseTaskModel, OperatorTask
from .bash import BashTask
from .custom import CustomTask
from .debug import DebugTask
from .empty import EmptyTask
from .python import PythonTask

Task = Annotated[
    Union[
        EmptyTask,
        DebugTask,
        BashTask,
        PythonTask,
        CustomTask,
    ],
    Field(
        discriminator="op",
        description="All supported Operator Tasks.",
    ),
]


class GroupTask(BaseTask):
    """Group of Task model that will represent Airflow Task Group object."""

    group: str = Field(description="A task group name.")
    tasks: list["AnyTask"] = Field(
        default_factory=list,
        description="A list of Any Task model.",
    )

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: dict[str, Any] | None = None,
        **kwargs,
    ) -> TaskGroup:
        """Build Airflow Task Group object."""
        task_group = TaskGroup(
            group_id=self.group, parent_group=task_group, dag=dag
        )
        tasks: dict[str, TaskMapped] = {}
        for task in self.tasks:
            task_object: Operator | TaskGroup = task.build(
                dag=dag, task_group=task_group, **kwargs
            )
            tasks[task.iden] = {
                "upstream": task.upstream,
                "task": task_object,
            }
        set_upstream(tasks)
        return task_group

    @property
    def iden(self) -> str:
        """Return Task Group Identity with it group name."""
        return self.group


AnyTask = Annotated[
    Union[
        Task,
        GroupTask,
    ],
    Field(
        union_mode="smart",
        description="An any task type that able operator task or group task.",
    ),
]
