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
        context: dict[str, Any] | None = None,
        **kwargs,
    ) -> Operator | TaskGroup:
        """Build with Custom builder function."""
        ctx: dict[str, Any] = context or {}
        custom_operators: dict[str, Any] = ctx["operators"]
        if self.uses not in custom_operators:
            raise ValueError(
                f"Custom task need to pass custom operator, {self.uses}, first."
            )
        return custom_operators[self.uses](
            dag=dag,
            task_group=task_group,
            context=context | self.params,
            **kwargs,
        )
