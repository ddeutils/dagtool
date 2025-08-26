import pytest
from airflow.exceptions import AirflowException
from airflow.operators.empty import EmptyOperator

from dagtool.tasks.empty import EmptyTask


def test_task_empty():
    task = EmptyTask(task="demo", op="empty")
    assert task.upstream == []
    assert task.task_kwargs() == {"task_id": "demo"}


def test_task_empty_build():
    task = EmptyTask(task="demo", op="empty")
    op = task.build()
    assert isinstance(op, EmptyOperator)
    assert op.task_id == "demo"

    with pytest.raises(AirflowException) as e:
        _ = op.dag
    assert "has not been assigned to a DAG yet" in str(e.value)
