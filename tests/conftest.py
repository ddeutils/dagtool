import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# NOTE: Set unittest config for Airflow.
os.environ["AIRFLOW__CORE__UNIT_TEST_MODE"] = "true"


@pytest.fixture(scope="package")
def test_path() -> Path:
    return Path(__file__).parent


@pytest.fixture(scope="package")
def root_path(test_path: Path) -> Path:
    return test_path.parent
