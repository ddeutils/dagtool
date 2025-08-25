from datetime import datetime

import pytest
from airflow.models import Variable


def test_get_variable():
    with pytest.raises(KeyError):
        Variable.get("test")


def test_pendulum():
    data = datetime.fromisoformat("2022-06-16 00:00:00")
    print(type(data))
    print(data)
