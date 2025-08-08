from abc import ABC, abstractmethod
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, field_validator


class BaseTask(BaseModel, ABC):
    name: str
    type: str
    upstream: list[str] | None = Field(
        default=None,
        description="A list of upstream task name or only task name.",
    )

    @field_validator(
        "upstream",
        mode="before",
        json_schema_input_type=str | list[str] | None,
    )
    def __prepare_upstream(cls, data: Any) -> Any:
        if data and isinstance(data, str):
            return [data]
        return data

    @abstractmethod
    def action(self): ...


class OpTask(BaseTask, ABC):
    type: Literal["task"]
    op: str


class EmptyTask(OpTask):
    op: Literal["empty"]

    def action(self): ...


class PythonTask(OpTask):
    op: Literal["python"]

    def action(self): ...


class BashTask(OpTask):
    op: Literal["bash"]

    def action(self): ...


class SparkTask(OpTask):
    op: Literal["spark"]

    def action(self): ...


class DockerTask(OpTask):
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
    type: Literal["group"]
    tasks: list["AnyTask"] = Field(default_factory=list)

    def action(self): ...


AnyTask = Annotated[
    Union[
        GroupTask,
        Task,
    ],
    Field(discriminator="type"),
]


class DokDagModel(BaseModel):
    name: str
    schedule: str
    authors: list[str]
    tags: list[str] = Field(
        default_factory=list,
        description="A list of tag.",
    )
    start_date: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    params: dict[str, str] = Field(default_factory=dict)
    tasks: list[AnyTask] = Field(
        default_factory=list,
        description="A list of any task, pure task or group task",
    )
