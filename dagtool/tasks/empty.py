from typing import Any, Literal

from airflow.models import DAG, Operator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

from .__abc import OperatorTask


class EmptyTask(OperatorTask):
    """Empty Task model."""

    op: Literal["empty"]

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: dict[str, Any] | None = None,
        **kwargs,
    ) -> Operator:
        """Build Airflow Empty Operator object."""
        return EmptyOperator(
            task_id=self.task,
            doc=self.desc,
            task_group=task_group,
            dag=dag,
            **kwargs,
        )
