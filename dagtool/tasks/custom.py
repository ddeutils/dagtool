from typing import Any, Literal

from airflow import DAG
from airflow.models import Operator
from airflow.utils.task_group import TaskGroup
from pydantic import Field

from .__abc import OperatorTask


class CustomTask(OperatorTask):
    """Custom Task."""

    op: Literal["custom"]
    uses: str = Field(description="A custom building function name.")
    params: dict[str, Any] = Field(default_factory=dict)

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        **kwargs,
    ) -> Operator | TaskGroup: ...
