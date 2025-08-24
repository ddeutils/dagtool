from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


@pytest.fixture(scope="package")
def test_path() -> Path:
    return Path(__file__).parent
