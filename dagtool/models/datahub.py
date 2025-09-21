from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any, Literal
from unittest.mock import MagicMock

try:
    from datahub_provider.entities import Dataset as DataHubDataset

    DATAHUB_PROVIDER_INSTALLED: bool = True
except ImportError:
    DataHubDataset = MagicMock
    DATAHUB_PROVIDER_INSTALLED: bool = False

from pydantic import BaseModel, Field

from ..utils import need_install

Platform = Literal[
    "hive",
    "gcs",
    "hdfs",
    "hana",
    "iceberg",
    "s3",
    "kafka",
    "kafka_connect",
    "mongodb",
    "mysql",
    "openapi",
    "postgres",
    "oracle",
    "tableau",
    "mssql",
    "bigquery",
    "druid",
    "file",
]
PLATFORM_MAPS: dict[Platform, str] = {
    "hive": "hive",
    "gcs": "gcs",
    "hdfs": "hdfs",
    "hana": "hana",
    "iceberg": "iceberg",
    "s3": "s3",
    "kafka": "kafka",
    "kafka_connect": "kafka-connect",
    "mongodb": "mongodb",
    "mysql": "mysql",
    "openapi": "OpenApi",
    "postgres": "postgres",
    "oracle": "oracle",
    "tableau": "tableau",
    "mssql": "mssql",
    "bigquery": "bigquery",
    "druid": "druid",
    "file": "file",
}


class BaseDataset(BaseModel, ABC):
    platform: Platform = Field(description="A platform type.")
    name: str = Field(description="An entity name.")

    @abstractmethod
    def build(self) -> Any:
        """Build Dataset object from these fields."""


class Dataset(BaseDataset):
    """DataHub Dataset model."""

    platform_instance: str | None = Field(default=None)

    @need_install(
        flag=DATAHUB_PROVIDER_INSTALLED,
        package="acryl-datahub-airflow-plugin",
    )
    def build(self) -> DataHubDataset:
        """Build a DataHub Dataset object.

        Returns:
            A Dataset object from Datahub provider that construct from this
                Dataset fields.
        """
        return DataHubDataset(
            platform=PLATFORM_MAPS[self.platform],
            name=self.name,
            # NOTE: An Environment value for Datahub should be uppercase.
            env=os.getenv("AIRFLOW_ENV", "dev").upper(),
            platform_instance=self.platform_instance,
        )
