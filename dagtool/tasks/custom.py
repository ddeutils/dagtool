from typing import Any, Literal

from airflow import DAG
from airflow.models import Operator
from airflow.utils.task_group import TaskGroup
from pydantic import Field

from .__abc import BaseTask, Context, OperatorTask


class CustomTask(OperatorTask):
    """Custom Task model."""

    op: Literal["custom"]
    uses: str = Field(description="A custom building function name.")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "A mapping of parameters that want to pass to Custom Task model "
            "before build."
        ),
    )

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Operator | TaskGroup:
        """Build with Custom builder function."""
        ctx: dict[str, Any] = context or {}
        custom_operators: dict[str, type[BaseTask]] = ctx["operators"]
        if self.uses not in custom_operators:
            raise ValueError(
                f"Custom task need to pass custom operator, {self.uses}, first."
            )
        op: type[BaseTask] = custom_operators[self.uses]
        model: BaseTask = op.model_validate(self.params)
        return model.build(
            dag=dag,
            task_group=task_group,
            context=context | self.params,
            **kwargs,
        )
