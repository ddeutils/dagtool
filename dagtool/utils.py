from typing import Any

from airflow.models.baseoperator import BaseOperator
from airflow.utils.context import Context


def clear_globals(gb: dict[str, Any]) -> dict[str, Any]:
    """Clear Globals variable support keeping necessary values only.

    Args:
        gb (dict[str, Any]): The globals variables.
    """
    return {k: gb[k] for k in gb if k not in ("__builtins__", "__cached__")}


class FreeOperator(BaseOperator):
    """Operator that does literally nothing.

    It can be used to group tasks in a DAG.
    The task is evaluated by the scheduler but never processed by the executor.
    """

    ui_color = "#e8f7e4"
    inherits_from_empty_operator = True

    def execute(self, context: Context):
        pass
