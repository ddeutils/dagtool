from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from ..loader import YamlConf
    from ..utils import TaskMapped
    from .tool import BaseOperator, ToolModel


class BuildContext(TypedDict):
    """Build Context type dict that wat generated from the Factory object before
    start building Airflow DAG from template config.
    """

    path: Path
    yaml_loader: YamlConf
    vars: dict[str, Any]
    tasks: dict[str, TaskMapped]
    tools: dict[str, type[ToolModel]]
    operators: dict[str, type[BaseOperator]]
    python_callers: dict[str, Callable]
    extras: dict[str, Any]
