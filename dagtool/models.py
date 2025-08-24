from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal, Union

from airflow.models import DAG
from pydantic import BaseModel, Field

from .plugins.tasks import AnyTask


class DefaultArgs(BaseModel):
    """Default Args Model that will use with the `default_args` field."""

    owner: str | None = None


class DagModel(BaseModel):
    """Base Dag Model for validate template config data support DagTool object.
    This model will include necessary field for Airflow DAG object and custom
    field for DagTool object together.
    """

    name: str = Field(description="A DAG name.")
    type: Literal["dag"] = Field(description="A type of template config.")
    docs: str | None = Field(
        default=None,
        description="A DAG document that allow to pass with markdown syntax.",
    )
    params: dict[str, str] = Field(default_factory=dict)
    tasks: list[AnyTask] = Field(
        default_factory=list,
        description="A list of any task, origin task or group task",
    )

    # NOTE: Runtime parameters that extract from YAML loader step.
    filename: str | None = Field(
        default=None,
        description="A filename of the current position.",
    )
    parent_dir: Path | None = Field(default=None, description="")
    created_dt: datetime | None = Field(default=None, description="")
    updated_dt: datetime | None = Field(default=None, description="")

    # NOTE: Airflow DAG parameters.
    owner: str = Field(default=None)
    tags: list[str] = Field(default_factory=list, description="A list of tags.")
    schedule: str | None = Field(default=None)
    start_date: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    concurrency: int | None = Field(default=None)
    max_active_runs: int = 1
    dagrun_timeout_sec: int = 600

    def build(
        self,
        prefix: str | None,
        default_args: dict[str, Any] | None = None,
    ) -> DAG:
        """Build Airflow DAG object.

        Args:
            prefix (str | None): A prefix of DAG name.
            default_args: (dict[str, Any]):
        """
        name: str = f"{prefix}_{self.name}" if prefix else self.name
        dag = DAG(
            dag_id=name,
            tags=self.tags,
            schedule=self.schedule,
            start_date=self.start_date,
            end_date=self.end_date,
            concurrency=self.concurrency,
            max_active_runs=self.max_active_runs,
            dagrun_timeout=timedelta(seconds=self.dagrun_timeout_sec),
            default_args={"owner": self.owner, **(default_args or {})},
        )
        return dag


Primitive = Union[str, int, float, bool]
ValueType = Union[Primitive, list[Primitive], dict[Union[str, int], Primitive]]


class Key(BaseModel):
    """Key Model."""

    key: str = Field(description="A key name.")
    desc: str | None = Field(
        default=None,
        description="A description of this variable.",
    )
    stages: dict[str, dict[str, ValueType]] = Field(
        default=dict,
        description="A stage mapping with environment and its pair of variable",
    )


class Variable(BaseModel):
    """Variable Model."""

    type: Literal["variable"] = Field(description="A type of variable model.")
    variables: list[Key] = Field(description="A list of Key model.")

    def get_key(self, name: str) -> Key:
        """Get the Key model with an input specific key name.

        Args:
            name (str): A key name.

        Returns:
            Key: A Key model.
        """
        for k in self.variables:
            if name == k.key:
                return k
        raise ValueError(f"A key: {name} does not set on this variables.")
