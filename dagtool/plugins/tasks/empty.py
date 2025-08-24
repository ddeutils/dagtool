import json
from collections.abc import Sequence
from typing import Any, Literal

from airflow.models import DAG, Operator
from airflow.models.baseoperator import BaseOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.context import Context
from airflow.utils.task_group import TaskGroup
from pydantic import Field

from .__abc import OperatorTask


class EmptyTask(OperatorTask):
    """Empty Task model."""

    op: Literal["empty"]

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        **kwargs,
    ) -> Operator:
        """Build Airflow Empty Operator object."""
        return EmptyOperator(
            task_id=self.task, task_group=task_group, dag=dag, **kwargs
        )


class DebugOperator(BaseOperator):
    """Operator that does literally nothing.

    It can be used to group tasks in a DAG.
    The task is evaluated by the scheduler but never processed by the executor.
    """

    ui_color: str = "#fcf5a2"
    inherits_from_empty_operator: bool = True
    template_fields: Sequence[str] = ("debug",)

    def __init__(self, debug: dict[str, Any], **kwargs) -> None:
        super().__init__(**kwargs)
        self.debug = debug

    def execute(self, context: Context) -> None:
        for k, v in self.debug.items():
            self.log.info(f"> {k}: {v}")
        self.log.info("Start DEBUG Context:")
        self.log.info(json.dumps(context, indent=1))


class DebugTask(OperatorTask):
    """Free Task model."""

    op: Literal["debug"]
    params: dict[str, Any] = Field(default_factory=dict)

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        **kwargs,
    ) -> Operator:
        """Build Airflow Debug Operator object."""
        return DebugOperator(
            task_id=self.task,
            task_group=task_group,
            dag=dag,
            debug=self.params,
            **kwargs,
        )
