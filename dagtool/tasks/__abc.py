from abc import ABC, abstractmethod
from typing import Any

from airflow.models import DAG, Operator
from airflow.utils.task_group import TaskGroup
from pydantic import BaseModel, Field, field_validator


class BaseTask(BaseModel, ABC):
    """Base Task model that represent Airflow Task object."""

    desc: str | None = Field(default=None)
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
        """
        if data is None:
            return []
        elif data and isinstance(data, str):
            return [data]
        return data

    @abstractmethod
    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: dict[str, Any] | None = None,
        **kwargs,
    ) -> Operator | TaskGroup:
        """Build Any Airflow Task object."""

    @property
    @abstractmethod
    def iden(self) -> str:
        """Task identity Abstract method."""


class OperatorTask(BaseTask, ABC):
    """Operator Task Model."""

    task: str = Field(description="A task name.")
    op: str = Field(description="An operator type of this task.")

    @abstractmethod
    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: dict[str, Any] | None = None,
        **kwargs,
    ) -> Operator:
        """Build the Airflow Operator object from this model fields."""

    @property
    def iden(self) -> str:
        return self.task
