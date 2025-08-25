from typing import Literal

from airflow.models import DAG, Operator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from pydantic import Field

from .__abc import OperatorTask


class BashTask(OperatorTask):
    """Bash Task model that will represent to Airflow BashOperator object."""

    op: Literal["bash"] = Field(description="An operator type for bash model.")
    bash_command: str = Field(description="A bash command or bash file")
    env: dict[str, str] | None = None
    append_env: bool = False
    output_encoding: str = "utf-8"
    skip_on_exit_code: int | list[int] | None = Field(default=99)
    cwd: str | None = None

    def build(
        self,
        dag: DAG | None = None,
        task_group: TaskGroup | None = None,
        **kwargs,
    ) -> Operator:
        """Build Airflow Bash Operator object."""
        return BashOperator(
            task_id=self.task,
            bash_command=self.bash_command,
            env=self.env,
            append_env=self.append_env,
            output_encoding=self.output_encoding,
            skip_on_exit_code=self.skip_on_exit_code,
            cwd=self.cwd,
            dag=dag,
            task_group=task_group,
        )
