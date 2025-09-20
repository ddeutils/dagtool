from __future__ import annotations

from typing import Annotated, Union

try:
    from airflow.sdk.definitions.taskgroup import TaskGroup as _TaskGroup
except ImportError:
    from airflow.utils.task_group import TaskGroup as _TaskGroup

from pydantic import Field

from .common.custom_tool import CustomToolTask
from .common.debug import DebugTask, RaiseTask
from .common.operator import OperatorTask
from .standard.bash import BashTask
from .standard.empty import EmptyTask
from .standard.python import PythonTask

Task = Annotated[
    Union[
        EmptyTask,
        DebugTask,
        BashTask,
        PythonTask,
        CustomToolTask,
        OperatorTask,
        RaiseTask,
    ],
    Field(
        discriminator="uses",
        description="All supported tasks.",
    ),
]
