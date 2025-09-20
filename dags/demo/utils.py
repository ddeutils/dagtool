import logging
from typing import TYPE_CHECKING, Any

try:
    from airflow.providers.standard.operators.empty import EmptyOperator
    from airflow.sdk.definitions.dag import DAG
    from airflow.sdk.definitions.taskgroup import TaskGroup
except ImportError:
    from airflow.models.dag import DAG
    from airflow.operators.empty import EmptyOperator
    from airflow.utils.task_group import TaskGroup

from pydantic import Field

from dagtool.models.tool import ToolModel
from dagtool.providers.common.operators.debug import DebugOperator

if TYPE_CHECKING:
    from dagtool.models.build_context import BuildContext


def say_hi(name: Any) -> str:
    """Custom Python function that will use with Airflow PythonOperator."""
    logging.info(f"Input: {name}")
    if not isinstance(name, str):
        logging.info(f"Hello {name.name}")
        return name.name if hasattr(name, "name") else str(name)

    logging.info(f"Hello {name}")
    return name


class CustomTool(ToolModel):
    """Custom Tool model."""

    name: str = Field(description="A name.")

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        build_context: BuildContext | None = None,
    ) -> TaskGroup:
        with TaskGroup(
            "custom_task_group",
            dag=dag,
            parent_group=task_group,
        ) as tg:
            start = EmptyOperator(task_id="start", dag=dag)
            t2 = DebugOperator(
                task_id=f"for_{self.name.lower()}",
                debug={"name": self.name},
                dag=dag,
            )
            start >> t2
        return tg
