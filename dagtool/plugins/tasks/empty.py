from typing import Literal

from airflow.models import DAG, Operator
from airflow.models.baseoperator import BaseOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.context import Context

from .__abc import OperatorTask


class EmptyTask(OperatorTask):
    """Empty Task model."""

    op: Literal["empty"]

    def build(self, dag: DAG | None = None, **kwargs) -> Operator:
        print(f"Start building Empty Task from DAG: {dag}")
        return EmptyOperator(task_id=self.task, dag=dag)


class DebugOperator(BaseOperator):
    """Operator that does literally nothing.

    It can be used to group tasks in a DAG.
    The task is evaluated by the scheduler but never processed by the executor.
    """

    ui_color = "#fcf5a2"
    inherits_from_empty_operator = True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        for k, v in kwargs:
            self.log.info(f"> {k}: {v}")

    def execute(self, context: Context):
        pass


class DebugTask(OperatorTask):
    """Free Task model."""

    op: Literal["debug"]

    def build(self, dag: DAG | None = None, **kwargs) -> Operator:
        return DebugOperator(task_id=self.task, dag=dag)
