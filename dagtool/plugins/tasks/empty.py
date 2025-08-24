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
        return EmptyOperator(task_id=self.task, dag=dag)


class FreeOperator(BaseOperator):
    """Operator that does literally nothing.

    It can be used to group tasks in a DAG.
    The task is evaluated by the scheduler but never processed by the executor.
    """

    ui_color = "#fcf5a2"
    inherits_from_empty_operator = True

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def execute(self, context: Context):
        pass


class FreeTask(OperatorTask):
    """Free Task model."""

    op: Literal["free"]

    def build(self, dag: DAG | None = None, **kwargs) -> Operator:
        return FreeOperator(task_id=self.task, dag=dag)
