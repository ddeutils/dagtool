from typing import Any, Literal

from airflow import DAG
from airflow.models import Operator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from pydantic import Field

from .__abc import OperatorTask


class PythonTask(OperatorTask):
    op: Literal["python"]
    func: str = Field(description="A Python function name.")
    params: dict[str, Any] = Field(default_factory=dict)

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: dict[str, Any] | None = None,
        **kwargs,
    ) -> Operator:
        """Build Airflow Python Operator object."""
        ctx: dict[str, Any] = context or {}
        python_callers: dict[str, Any] = ctx["python_callers"]
        if self.func not in python_callers:
            raise ValueError(
                f"Python task need to pass python callers function, "
                f"{self.func}, first."
            )
        return PythonOperator(
            task_id=self.task,
            doc=self.desc,
            task_group=task_group,
            dag=dag,
            python_callable=python_callers[self.func],
            op_kwargs=self.params,
            **kwargs,
        )
