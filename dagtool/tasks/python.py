from typing import Literal

from airflow import DAG
from airflow.models import Operator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from pydantic import Field

from .__abc import OperatorTask


class PythonTask(OperatorTask):
    op: Literal["python"]
    func: str = Field(description="A Python function name.")

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        **kwargs,
    ) -> Operator:
        return PythonOperator(
            task_id=self.task,
            doc=self.desc,
            task_group=task_group,
            dag=dag,
            **kwargs,
        )
