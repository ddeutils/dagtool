from pathlib import Path

import pytest
from yaml import safe_load

from dedag.models import DokDagModel


@pytest.fixture(scope="module")
def demo_data(test_path: Path):
    return safe_load((test_path / "demo/demo_config.yml").open(mode="rt"))


def test_dokdag_model(demo_data):
    print(demo_data)
    model = DokDagModel.model_validate(demo_data)
    print(model)
