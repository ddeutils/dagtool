from __future__ import annotations

from datetime import datetime, timedelta
from functools import partial
from typing import Any

from airflow.configuration import conf as airflow_conf
from airflow.utils.trigger_rule import TriggerRule
from pydantic import BaseModel, ConfigDict, Field


class DefaultArgs(BaseModel):
    """Default Args Model that will use with the `default_args` field with the
    Airflow DAG object. These field reference arguments from the BaseOperator
    object.
    """

    model_config = ConfigDict(use_enum_values=True)

    owner: str | None = Field(default=None, description="An owner name.")
    depends_on_past: bool = Field(default=False, description="")
    start_date: datetime | None = None
    end_date: datetime | None = None
    email: str | list[str] | None = Field(
        default=None,
        description=(
            "the 'to' email address(es) used in email alerts. This can be a "
            "single email or multiple ones. Multiple addresses can be "
            "specified as a comma or semicolon separated string or by passing "
            "a list of strings."
        ),
    )
    email_on_failure: bool = Field(
        default_factory=partial(
            airflow_conf.getboolean,
            "email",
            "default_email_on_failure",
            fallback=True,
        ),
        description=(
            "Indicates whether email alerts should be sent when a task failed"
        ),
    )
    email_on_retry: bool = Field(
        default_factory=partial(
            airflow_conf.getboolean,
            "email",
            "default_email_on_retry",
            fallback=True,
        ),
    )
    retries: int = Field(
        default_factory=partial(
            airflow_conf.getint,
            "core",
            "default_task_retries",
            fallback=0,
        ),
        description="A retry count number.",
    )
    retry_delay: dict[str, int] | None = Field(
        default_factory=partial(
            timedelta,
            seconds=airflow_conf.getint(
                "core",
                "default_task_retry_delay",
                fallback=300,
            ),
        ),
        description="A retry time delay before start the next retry process.",
    )
    retry_exponential_backoff: bool = Field(
        default=False,
        description=(
            "allow progressively longer waits between retries by using "
            "exponential backoff algorithm on retry delay (delay will be "
            "converted into seconds)."
        ),
    )
    max_retry_delay: float | None = None
    # queue = ...
    # pool = ...
    # priority_weight = ...
    # weight_rule = ...
    # wait_for_downstream = ...
    trigger_rule: TriggerRule = Field(
        default=TriggerRule.ALL_SUCCESS,
        description=(
            "Task trigger rule. Read more detail, "
            "https://www.astronomer.io/blog/understanding-airflow-trigger-rules-comprehensive-visual-guide/"
        ),
    )
    # execution_timeout = ...
    # on_failure_callback = ...
    # on_success_callback = ...
    # on_retry_callback = ...
    sla: Any | None = Field(default=None)
    # sla_miss_callback = ...
    # executor_config = ...
    do_xcom_push: bool = Field(default=True)

    def to_dict(self) -> dict[str, Any]:
        """Making Python dict object without field that use default value.

        Returns:
            dict[str, Any]: A mapping of this default args values.
        """
        return self.model_dump(exclude_defaults=True)
