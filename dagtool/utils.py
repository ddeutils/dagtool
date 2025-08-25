import os
from datetime import datetime
from typing import Any, TypedDict
from zoneinfo import ZoneInfo

from airflow.models import Operator, Variable
from airflow.utils.task_group import TaskGroup
from pendulum import DateTime


def clear_globals(gb: dict[str, Any]) -> dict[str, Any]:
    """Clear Globals variable support keeping necessary values only.

    Args:
        gb (dict[str, Any]): The globals variables.
    """
    return {k: gb[k] for k in gb if k not in ("__builtins__", "__cached__")}


class TaskMapped(TypedDict):
    """Task Mapped dict typed."""

    upstream: list[str]
    task: Operator | TaskGroup


def set_upstream(tasks: dict[str, TaskMapped]) -> None:
    """Set Upstream Task for each tasks in mapping."""
    for task in tasks:
        task_mapped: TaskMapped = tasks[task]
        if upstream := task_mapped["upstream"]:
            for t in upstream:
                task_mapped["task"].set_upstream(tasks[t]["task"])


def get_var(key: str) -> str | None:
    """Get Airflow Variable."""
    return Variable.get(key)


def get_env(key: str) -> str | None:
    return os.getenv(key, None)


def change_tz(dt: datetime | DateTime, tz: str = "UTC") -> datetime | DateTime:
    if isinstance(dt, datetime):
        return dt.astimezone(ZoneInfo(tz))
    return dt.in_timezone(tz)


def format_dt(dt: datetime | DateTime, fmt: str = "%Y-%m-%d %H:00:00%z") -> str:
    return dt.strftime(fmt)
