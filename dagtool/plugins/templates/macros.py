import os

from airflow.models import Variable


def get_var(key: str) -> str | None:
    """Get Airflow Variable."""
    return Variable.get(key)


def get_env(key: str) -> str | None:
    return os.getenv(key, None)
