from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal, Union

from pydantic import BaseModel, Field, ValidationError
from typing_extensions import Self
from yaml.parser import ParserError as YamlParserError

Primitive = Union[str, int, float, bool]
ValueType = Union[Primitive, list[Primitive], dict[Union[str, int], Primitive]]


class Key(BaseModel):
    """Key Model that use to store multi-stage variable with a specific key."""

    key: str = Field(
        description="A key name that will equal with the DAG name.",
    )
    desc: str | None = Field(
        default=None,
        description="A description of this variable.",
    )
    stages: dict[str, dict[str, ValueType]] = Field(
        default=dict,
        description="A stage mapping with environment and its pair of variable",
    )


class Variable(BaseModel):
    """Variable Model."""

    type: Literal["variable"] = Field(description="A type of this variable.")
    variables: list[Key] = Field(description="A list of Key model.")

    @classmethod
    def from_path(cls, path: Path) -> Self:
        from ..loader import YamlConf

        return cls.model_validate(YamlConf(path=path).read_vars())

    @classmethod
    def from_path_with_key(cls, path: Path, key: str) -> dict[str, Any]:
        """Get Variable stage from path.

        Args:
            path (Path): A template path.
            key (str): A key name that want to get from Variable model.

        Returns:
            dict[str, Any]: A mapping of variables that set on the current stage.
                It will return empty dict if it raises FileNotFoundError and
                ValueError exceptions.
        """
        try:
            return (
                cls.from_path(path=path)
                .get_key(key)
                .stages.get(os.getenv("AIRFLOW_ENV", "NOTSET"), {})
            )
        except FileNotFoundError:
            return {}
        except YamlParserError:
            raise
        except ValidationError:
            raise
        except ValueError:
            return {}

    def get_key(self, name: str) -> Key:
        """Get the Key model with an input specific key name.

        Args:
            name (str): A key name.

        Raises:
            ValueError: If the key does not exist on this Variable model.

        Returns:
            Key: A Key model.
        """
        for k in self.variables:
            if name == k.key:
                return k
        raise ValueError(f"A key: {name} does not set on this variables.")
