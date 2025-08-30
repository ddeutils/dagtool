import pytest
from airflow.exceptions import AirflowException

try:
    from airflow.providers.standard.operators.empty import EmptyOperator
    from airflow.utils.trigger_rule import TriggerRule
except ImportError:
    from airflow.operators.empty import EmptyOperator
    from airflow.utils.trigger_rule import TriggerRule

from dagtool.tasks.empty import EmptyTask
from dagtool.utils import AIRFLOW_VERSION


def test_tool_empty():
    task = EmptyTask(task="demo", uses="empty")
    assert task.upstream == []
    assert task.task_kwargs() == {
        "task_id": "demo",
        "retry_exponential_backoff": False,
        "trigger_rule": TriggerRule.ALL_SUCCESS,
    }


def test_tool_empty_build():
    task = EmptyTask(task="demo", uses="empty")
    op = task.build()
    assert isinstance(op, EmptyOperator)
    assert op.task_id == "demo"

    if AIRFLOW_VERSION >= [3, 0, 0]:
        with pytest.raises(RuntimeError) as e:
            _ = op.dag
        assert "has not been assigned to a DAG yet" in str(e.value)
    else:
        with pytest.raises(AirflowException) as e:
            _ = op.dag
        assert "has not been assigned to a DAG yet" in str(e.value)
