import logging
from typing import Any

from airflow import DAG
from airflow.models import Operator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

from dagtool.tasks import BaseTaskModel
from dagtool.tasks.debug import DebugOperator


def say_hi(name: str) -> str:
    logging.info(f"Hello {name}")
    return name


class CustomTask(BaseTaskModel):
    name: str

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        context: dict[str, Any] | None = None,
        **kwargs,
    ) -> Operator | TaskGroup:
        with TaskGroup(
            "custom_task_group", dag=dag, parent_group=task_group
        ) as tg:
            t1 = EmptyOperator(task_id="start", dag=dag)
            t2 = DebugOperator(
                task_id=f"for_{self.name.lower()}",
                dag=dag,
                debug={"name": self.name},
            )
            t1 >> t2
        return tg
