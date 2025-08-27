from pathlib import Path

import pytest
from yaml import safe_load

from dagtool.models import DagModel


@pytest.fixture(scope="module")
def demo_data(test_path: Path):
    return safe_load((test_path / "demo/demo_config.yml").open(mode="rt"))


def test_model(demo_data):
    print(demo_data)
    model = DagModel.model_validate(demo_data)
    print(model)
