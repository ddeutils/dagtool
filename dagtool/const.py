import os
from typing import Final

AIRFLOW_ENV: Final[str] = os.getenv("AIRFLOW_ENV", "dev")
DAG_ID_KEY: Final[str] = "id"
DAG_FILENAME_PREFIX: Final[str] = "dag"
VARIABLE_FILENAME: Final[str] = "variables"
ASSET_DIR: Final[str] = "assets"
SYNC_DIR: Final[str] = "sync"
