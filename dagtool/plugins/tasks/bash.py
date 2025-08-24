from typing import Literal

from airflow.models import DAG, Operator
from airflow.operators.bash import BashOperator
from pydantic import Field

from .__abc import OperatorTask


class BashTask(OperatorTask):
    """Bash Task model that will represent to Airflow BashOperator object."""

    op: Literal["bash"] = Field(description="An operator type for bash model.")
    bash_command: str = Field(description="A bash command or bash file")
    env: dict[str, str] | None = None
    append_env: bool = False
    output_encoding: str = "utf-8"
    skip_on_exit_code: int | list[int] | None = None
    cwd: str | None = None

    def build(self, dag: DAG | None = None, **kwargs) -> Operator:
        """Build."""
        return BashOperator(
            task_id=self.task,
            bash_command=self.bash_command,
            env=self.env,
            dag=dag,
        )
