from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal

from airflow.models import DAG
from pydantic import BaseModel, Field

from .operators import AnyTask


class DagModel(BaseModel):
    """Base DeDag Model for validate template config data."""

    name: str = Field(description="A DAG name.")
    type: Literal["dag"] = Field(description="A type of template config.")
    docs: str | None = Field(default=None, description="A DAG document.")
    params: dict[str, str] = Field(default_factory=dict)
    tasks: list[AnyTask] = Field(
        default_factory=list,
        description="A list of any task, pure task or group task",
    )

    # NOTE: Runtime parameters.
    filename: str | None = Field(default=None)
    parent_dir: Path | None = Field(default=None, description="")
    created_dt: datetime | None = Field(default=None, description="")
    updated_dt: datetime | None = Field(default=None, description="")

    # NOTE: Airflow DAG parameters.
    owner: str = Field(default=None)
    tags: list[str] = Field(default_factory=list, description="A list of tags.")
    schedule: str
    start_date: str | None = Field(default=None)
    end_date: str | None = Field(default=None)
    concurrency: int | None = Field(default=None)
    max_active_runs: int = 1
    dagrun_timeout_sec: int = 600

    def build(
        self, prefix: str | None, default_args: dict[str, Any] | None = None
    ) -> DAG:
        """Build Airflow DAG object."""
        name: str = f"{prefix}_{self.name}" if prefix else self.name
        dag = DAG(
            dag_id=name,
            tags=self.tags,
            schedule=self.schedule,
            start_date=self.start_date,
            end_date=self.end_date,
            concurrency=self.concurrency,
            max_active_runs=self.max_active_runs,
            dagrun_timeout=timedelta(seconds=self.dagrun_timeout_sec),
            default_args={"owner": self.owner, **(default_args or {})},
        )
        return dag
