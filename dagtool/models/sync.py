from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

StorageType = Literal["local", "gcs", "s3", "adls"]


class Storage(BaseModel):
    type: StorageType
    path: str
    excluded: list[str] = Field(default_factory=list)


class Key(BaseModel):
    key: str = Field(description="A key name.")
    stages: dict[str, Storage]


class Sync(BaseModel):
    """Sync model."""

    type: Literal["sync"] = Field(description="A sync type.")
    sync: list[Key] = Field(default_factory=list, description="A list of key.")
