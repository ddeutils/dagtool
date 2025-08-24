from typing import Annotated, Union

from airflow.utils.task_group import TaskGroup
from pydantic import Field

from .__abc import BaseTask
from .bash import BashTask
from .empty import DebugTask, EmptyTask

Task = Annotated[
    Union[
        EmptyTask,
        DebugTask,
        # PythonTask,
        BashTask,
        # SparkTask,
        # DockerTask,
    ],
    Field(discriminator="op"),
]


class GroupTask(BaseTask):
    """Group of Task model that will represent Airflow Task Group object."""

    group: str = Field(description="A task group name.")
    tasks: list["AnyTask"] = Field(
        default_factory=list,
        description="A list of Any Task model.",
    )

    def build(self) -> TaskGroup:
        """Build Task Group object."""
        with TaskGroup(group_id=self.group) as tg:
            pass

        return tg

    @property
    def iden(self) -> str:
        return self.group


AnyTask = Annotated[
    Union[
        Task,
        GroupTask,
    ],
    Field(union_mode="smart"),
]
