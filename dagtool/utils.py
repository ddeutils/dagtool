from __future__ import annotations

import hashlib
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, ClassVar, Final, TypeAlias, TypedDict, Union

try:
    from airflow.sdk.bases.operator import BaseOperator
    from airflow.sdk.definitions.taskgroup import TaskGroup
except ImportError:
    from airflow.models.baseoperator import BaseOperator
    from airflow.utils.task_group import TaskGroup

from airflow.version import version as airflow_version
from pendulum import DateTime

OperatorOrTaskGroup: TypeAlias = Union[BaseOperator, TaskGroup]


class TaskMapped(TypedDict):
    """Task Mapped dict typed."""

    upstream: list[str]
    task: OperatorOrTaskGroup


def set_upstream(tasks: dict[str, TaskMapped]) -> None:
    """Set Upstream Task for each tasks in mapping.

    Args:
        tasks (dict[str, TaskMapped]):
            A mapping of task ID and TaskMapped dict object.
    """
    for task in tasks:
        task_mapped: TaskMapped = tasks[task]
        if upstream := task_mapped["upstream"]:
            for t in upstream:
                try:
                    task_mapped["task"].set_upstream(tasks[t]["task"])
                except KeyError as e:
                    raise KeyError(
                        f"Task ids, {e}, does not found from the template.\n"
                        f"The current task key: {list(tasks.keys())}"
                    ) from e


def get_id(obj: OperatorOrTaskGroup) -> str:
    """Return task ID if it does not be TaskGroup instance otherwise group ID.

    Args:
        obj: Any Airflow Operator or TaskGroup object.
    """
    return obj.group_id if isinstance(obj, TaskGroup) else obj.task_id


def change_tz(dt: DateTime | None, tz: str = "UTC") -> DateTime | None:
    """Change timezone to pendulum.DateTime object."""
    if dt is None:
        return None
    return dt.in_timezone(tz)


def format_dt(
    dt: datetime | DateTime | None, fmt: str = "%Y-%m-%d %H:00:00%z"
) -> str | None:
    """Format string value on pendulum.DateTime or datetime object"""
    if dt is None:
        return None
    return dt.strftime(fmt)


def random_str(n: int = 6) -> str:
    """Random charactor with specific length."""
    return uuid.uuid4().hex[:n].lower()


# NOTE: Defined builtin filters for this package.
FILTERS: Final[dict[str, Callable]] = {
    "tz": change_tz,
    "fmt": format_dt,
    "random_str": random_str,
}


def hash_sha256(data: str | bytes) -> str:
    """Calculates the SHA-256 hash of the given data.

    Args:
        data (str or bytes): The input data to be hashed.

    Returns:
        str: The hexadecimal representation of the SHA-256 hash.
    """
    if isinstance(data, str):
        # NOTE: Encode string to bytes
        data = data.encode("utf-8")

    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    return sha256_hash.hexdigest()


def days_ago(n, hour=0, minute=0, second=0, microsecond=0):
    """Get a datetime object representing `n` days ago. By default, the time is
    set to midnight.
    """
    today = datetime.now().replace(
        hour=hour, minute=minute, second=second, microsecond=microsecond
    )
    return today - timedelta(days=n)


def parse_version(version: str) -> list[int]:
    """Simple parse version string value to list of version that cast to integer
    type.

    Args:
        version (str): A version string.

    Returns:
        list[str]: A list of version.
    """
    vs: list[str] = version.split(".")
    return [int(vs[_]) for _ in range(3)]


AIRFLOW_VERSION: list[int] = parse_version(airflow_version)


def clear_globals(gb: dict[str, Any]) -> dict[str, Any]:
    """Clear Globals variable support keeping necessary values only.

    Args:
        gb (dict[str, Any]): A globals value.

    Returns:
        dict[str, Any]: A filtered globals value.
    """
    return {k: gb[k] for k in gb if k not in ("__builtins__", "__cached__")}


class DotDict(dict):
    """Dictionary with dot-notation get/set methods.

    Supports nested key lookup/set using dot-separated strings.
        - Strict mode: raises KeyError if missing
        - Safe mode: use '?' to skip missing keys
    """

    char_safe_mode: ClassVar[str] = "?"

    def __getitem__(self, item) -> Any:
        if not isinstance(item, str):
            return super().__getitem__(item)

        if "." not in item:
            return super().__getitem__(item)

        return self.get(key=item.replace("?", ""), strict=True)

    def get(
        self,
        key,
        default: Any | None = None,
        strict: bool = False,
    ) -> Any | None:
        """Getter dict method override to the ``get`` method on parent dict
        object.

        Args:
            key:
            default:
            strict:
        """

        if not isinstance(key, str):
            return super().get(key, default)

        if "." not in key:
            return super().get(key.replace("?", ""), default)

        keys: list[str] = key.split(".")
        value = self
        # Archive: Disable strict mode.
        # strict: bool = True

        for k in keys:
            safe: bool = k.endswith("?")
            if safe:
                strict: bool = False
                k = k[:-1]

            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                if strict:
                    raise KeyError(f"Key path '{key}' not found.")
                return default
        return value

    def set(self, key, value: Any | None) -> None:
        """Setter dict method."""

        if not isinstance(key, str):
            self[key] = value
            return

        if "." not in key:
            self[key.replace("?", "")] = value
            return

        keys: list[str] = key.split(".")
        d = self
        strict: bool = True

        for k in keys[:-1]:
            safe = k.endswith("?")
            if safe:
                strict = False
                k = k[:-1]

            if k not in d:
                if strict:
                    raise KeyError(f"Key path '{key}' not found")
                d[k] = {}
            d = d[k]

            if not isinstance(d, dict):
                raise TypeError(f"Path '{k}' is not a dict")

        last_key = keys[-1]
        if last_key.endswith("?"):
            strict: bool = False
            last_key = last_key[:-1]

        if strict and last_key not in d:
            raise KeyError(f"Key path '{key}' not found")

        d[last_key] = value


def need_install(flag: bool, package: str) -> Any:
    """Checking needed deps before call building method.

    Args:
        flag (bool): A flag that making from import layer. It should be True if
            the needed package already install in the current Python env.
        package (str): A package name that need to install.
    """

    def decorator(method) -> Any:
        @wraps(method)
        def wrapper(self, *args, **kwargs) -> Any:
            if flag:
                return method(self, *args, **kwargs)

            raise NotImplementedError(
                f"{self.__class__.__name__} need to install {package!r} "
                f"package first."
            )

        return wrapper

    return decorator
