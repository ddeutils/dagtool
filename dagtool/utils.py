from typing import Any, TypedDict

from airflow.models import Operator
from airflow.models.baseoperator import BaseOperator
from airflow.utils.task_group import TaskGroup


def clear_globals(gb: dict[str, Any]) -> dict[str, Any]:
    """Clear Globals variable support keeping necessary values only.

    Args:
        gb (dict[str, Any]): The globals variables.
    """
    return {k: gb[k] for k in gb if k not in ("__builtins__", "__cached__")}


class TaskMapped(TypedDict):
    upstream: list[str]
    task: Operator | BaseOperator | TaskGroup


def set_upstream(tasks: dict[str, TaskMapped]):
    for task in tasks:
        task_mapped: TaskMapped = tasks[task]
        if upstream := task_mapped["upstream"]:
            for t in upstream:
                task_mapped["task"].set_upstream(tasks[t]["task"])
