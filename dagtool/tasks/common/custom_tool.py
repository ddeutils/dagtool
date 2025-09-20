from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field

from dagtool.models.task import TaskModel

if TYPE_CHECKING:
    from dagtool.models.task import (
        DAG,
        BuildContext,
        OperatorOrTaskGroup,
        TaskGroup,
        ToolModel,
    )


class CustomToolTask(TaskModel):
    """Custom Task model."""

    uses: Literal["custom_tool"] = Field(description="A custom tool type.")
    name: str = Field(description="A custom tool name.")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "A mapping of parameters that want to pass to Custom Task model "
            "before build."
        ),
    )

    def build(
        self,
        dag: DAG,
        task_group: TaskGroup | None = None,
        build_context: BuildContext | None = None,
    ) -> OperatorOrTaskGroup:
        """Build with Custom tool builder method.

        Args:
            dag (DAG): An Airflow DAG object.
            task_group (TaskGroup, default None): An Airflow TaskGroup object
                if this task build under the task group.
            build_context (BuildContext, default None):
                A Context data that was created from the DAG Generator object.
        """
        ctx: BuildContext = build_context or {}
        custom_tasks: dict[str, type[ToolModel]] = ctx["tools"]
        if self.name not in custom_tasks:
            raise ValueError(
                f"Custom task need to pass to `tools` argument, {self.name}, "
                f"first."
            )
        op: type[ToolModel] = custom_tasks[self.name]
        model: ToolModel = op.model_validate(self.params)
        return model.build(
            dag=dag,
            task_group=task_group,
            build_context=build_context | self.params,
        )
