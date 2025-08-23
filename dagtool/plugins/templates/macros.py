from airflow.models import Variable


def get_var(key: str) -> str | None:
    """Get Airflow Variable."""
    return Variable.get(key)
