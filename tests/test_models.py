from pathlib import Path

import pytest
from pendulum import date, timezone
from yaml import safe_load

from dagtool.models.dag import Dag


@pytest.fixture(scope="module")
def demo_data(test_path: Path):
    return safe_load((test_path / "demo/dag_config.yml").open(mode="rt"))


def test_model():
    model = Dag(name="test", type="dag")
    assert model.name == "test"
    assert model.start_date is None
    assert model.end_date is None


def test_model_demo(demo_data):
    model = Dag.model_validate(demo_data)
    assert model.name == "sales_dag"
    print(model)


def test_model_convert_fields():
    model = Dag.model_validate(
        {
            "name": "dag_start_date",
            "type": "dag",
            "start_date": "2025-01-01 00:12:59",
        }
    )
    print(model.start_date)
    assert model.start_date.date() == date(2025, 1, 1)
    assert model.start_date.tzinfo == timezone("Asia/Bangkok")


def test_model_example_stock(root_path: Path):
    data = safe_load(
        (root_path / "dags/stock/stock_loss/dag_stock_loss.yml").open(mode="rt")
    )
    data["start_date"] = None
    data["max_active_runs"] = 1
    model = Dag.model_validate(data)
    print(model)
