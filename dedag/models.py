from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, field_validator


class BaseTask(BaseModel, ABC):
    upstream: list[str] | None = Field(
        default=None,
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
        """
        if data and isinstance(data, str):
            return [data]
        return data

    @abstractmethod
    def action(self): ...


class CoreTask(BaseTask, ABC):
    task: str = Field(description="A task name.")
    op: str = Field(description="An operator type of this task.")


class EmptyTask(CoreTask):
    op: Literal["empty"]

    def action(self): ...


class PythonTask(CoreTask):
    op: Literal["python"]

    def action(self): ...


class BashTask(CoreTask):
    op: Literal["bash"]

    def action(self): ...


class SparkTask(CoreTask):
    op: Literal["spark"]

    def action(self): ...


class DockerTask(CoreTask):
    op: Literal["docker"]

    def action(self): ...


Task = Annotated[
    Union[
        EmptyTask,
        PythonTask,
        BashTask,
        SparkTask,
        DockerTask,
    ],
    Field(discriminator="op"),
]


class GroupTask(BaseTask):
    group: str = Field(description="A task group name.")
    tasks: list["AnyTask"] = Field(
        default_factory=list,
        description="A list of Any Task model.",
    )

    def action(self): ...


AnyTask = Annotated[
    Union[
        Task,
        GroupTask,
    ],
    Field(union_mode="smart"),
]


class DagModel(BaseModel):
    """Base DeDag Model for validate template config data."""

    name: str = Field(description="A DAG name.")
    type: Literal["dag"] = Field(description="A type of template config.")
    docs: str | None = Field(default=None, description="A DAG document.")
    # authors: list[str] = Field(
    #     default_factory=list, description="A list of authors"
    # )
    params: dict[str, str] = Field(default_factory=dict)
    tasks: list[AnyTask] = Field(
        default_factory=list,
        description="A list of any task, pure task or group task",
    )

    # NOTE: Runtime parameters.
    filename: str | None = Field(default=None)
    parent_dir: Path | None = Field(default=None, description="")
    created_dt: datetime | None = Field(default=None, description="")
    updated_dt: datetime | None = Field(default=None, description="")

    # NOTE: Airflow DAG parameters.
    owner: str = Field(default=None)
    tags: list[str] = Field(default_factory=list, description="A list of tags.")
    schedule: str
    start_date: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    concurrency: int | None = Field(default=None)
    max_active_runs: int = 1
    dagrun_timeout_sec: int = 600
