import logging
import os
from pathlib import Path
from typing import Any

try:
    from airflow.sdk.definitions.variable import Variable as AirflowVariable
    from airflow.sdk.exceptions import AirflowRuntimeError
except ImportError:
    from airflow.models import Variable as AirflowVariable

    # NOTE: Mock AirflowRuntimeError with RuntimeError.
    AirflowRuntimeError = RuntimeError

from pydantic import ValidationError
from yaml import safe_load
from yaml.parser import ParserError

from .const import (
    ASSET_DIR,
    DAG_FILENAME_PREFIX,
    DAG_ID_KEY,
    SYNC_DIR,
    VARIABLE_FILENAME,
)
from .utils import hash_sha256

logger = logging.getLogger("common.conf")


class YamlConf:
    """Core Config object that use to find and map data from the current path.

    Attributes:
        path (Path): A filepath of template.
    """

    def __init__(self, path: Path | str) -> None:
        """Main initial construct method.

        Args:
            path (Path | str): A template config data.
        """
        self.path: Path = Path(path)

    def read_vars(self) -> dict[str, Any]:
        """Get Variable value with an input stage name.

        Raises:
            FileNotFoundError: If the variable file does not found in this
                template path.
            TypeError: If the type of variable content from parsing is list not
                dict type.
            ValueError: If the content data that read from file was emptied.

        Returns:
            dict[str, Any]: A mapping variable content that read with YAML file
                format.
        """
        search_files: list[Path] = list(
            self.path.rglob(f"{VARIABLE_FILENAME}.y*ml")
        )
        if not search_files:
            raise FileNotFoundError("Does not found variables file.")
        try:
            raw_data = safe_load(
                min(
                    search_files,
                    key=lambda f: len(str(f.absolute())),
                ).open(mode="rt", encoding="utf-8")
            )
            if not raw_data:
                raise ValueError("Variable file does not contain any content.")
            elif isinstance(raw_data, list):
                raise TypeError(
                    "Variable file should contain only mapping data not list "
                    "of data."
                )
            return raw_data
        except ParserError:
            raise

    def read_dag_conf(
        self,
        pre_validate: bool = True,
        only_one_dag: bool = False,
    ) -> list[dict[str, Any]]:
        """Read DAG template config from the path argument and reload to the
        conf.

        Args:
            pre_validate (bool, default True):
            only_one_dag (bool, default False): It will raise ValueError if the
                template dag config data fetch more than one.

        Returns:
            list[dict[str, Any]]: A list of model data before validate step.
        """
        from dagtool.models.dag import Dag

        conf: list[dict[str, Any]] = []
        for file in self.path.rglob("*"):
            logger.debug(f"Get object: {file}")
            if (
                file.is_file()
                and file.stem != VARIABLE_FILENAME
                and file.stem.startswith(DAG_FILENAME_PREFIX)
                and file.suffix in (".yml", ".yaml")
            ):
                try:
                    raw_data: str = file.read_text(encoding="utf-8")
                    data: dict[str, Any] | list[Any] = safe_load(raw_data)
                except ParserError:
                    logger.error(f"YAML file was not parsing, {file}.")
                    continue
                except Exception as e:
                    logger.error(f"YAML file got error, {e}, {file}.")
                    continue

                # VALIDATE: Does not support for empty data or list of template
                #   config.
                if not data or isinstance(data, list):
                    continue

                try:
                    if (
                        DAG_ID_KEY not in data
                        or data.get("type", "NOTSET") != "dag"
                    ):
                        continue

                    file_stats = file.stat()
                    model: dict[str, Any] = {
                        "filename": file.name,
                        "parent_dir": file.parent,
                        "created_dt": file_stats.st_ctime,
                        "updated_dt": file_stats.st_mtime,
                        "raw_data": raw_data,
                        "raw_data_hash": hash_sha256(raw_data),
                        **data,
                    }
                    logger.info(
                        f"Load DAG Template data: {model[DAG_ID_KEY]!r}"
                    )

                    # NOTE: Prevalidate DAG template data before keeping config.
                    if pre_validate:
                        Dag.model_validate(model)

                    conf.append(model)
                except AttributeError as err:
                    # NOTE: Except case data is not be `dict` type.
                    logger.error(f"Data does not read as dict.\n{err}")
                    continue
                except ValidationError as err:
                    logger.error(f"Prevalidate template data:\n{err}")
                    raise

        if len(conf) == 0:
            logger.warning(
                "Read config file from this template path does not exists"
            )
        if only_one_dag and len(conf) > 1:
            logger.error(
                f"DAG template data should contain only one DAG per folder:\n"
                f"{conf}."
            )
            raise ValueError(
                "DAG template data should contain only one DAG per folder."
            )
        return conf

    def read_assets(self, filename: str) -> str:
        """Read the asset file from the template config path.

        Args:
            filename (str): A specific filename that want to read from the
                assets template path.

        Returns:
            str: A content data that reading from the target asset file.
        """
        search_files: list[Path] = list(
            self.path.rglob(f"{ASSET_DIR}/{filename}")
        )
        if not search_files:
            raise FileNotFoundError(f"Asset file: {filename} does not found.")
        return search_files[0].read_text(encoding="utf-8")

    def read_sync(self, env: str | None = None) -> dict[str, str | bytes]:
        """Read Sync file mapping from the current template path.

        Args:
            env (str, default None):
                An environment value that want to read sync files.
        """
        _env: str = (env or os.getenv("AIRFLOW_ENV")).lower()
        search_files: list[Path] = list(self.path.rglob(f"{SYNC_DIR}/{_env}/*"))
        if not search_files:
            logger.warning("Sync files does not set.")
            return {}
        return {
            path.name: path.read_text(encoding="utf-8") for path in search_files
        }


def pull_vars(name: str, path: Path, prefix: str | None) -> dict[str, Any]:
    """Pull Variable. This method try to pull variable from Airflow Variable
    first. If it does not exist it will load from local file instead.

    Args:
        name (str): A name.
        path (Path): A template path that want to search variable file.
        prefix (str, default None): A prefix name that use to combine with name.

    Returns:
        dict[str, Any]: A variable mapping. This method will return empty dict
            if it gets any exceptions.
    """
    try:
        _name: str = f"{prefix}_{name}" if prefix else name
        raw_var: str = AirflowVariable.get(_name, deserialize_json=False)
        var: dict[str, Any] = safe_load(raw_var)
        return var
    except (
        KeyError,
        # NOTE: Raise from Airflow version >= 3.0.0 instead of KeyError.
        AirflowRuntimeError,
    ):
        pass
    except ImportError as err:  # NOTE: Raise from Airflow version >= 3.0.0
        if "cannot import name 'SUPERVISOR_COMMS'" not in str(err):
            raise
        pass

    from .models.variable import Variable

    try:
        return Variable.from_path_with_key(path, key=name)
    except ParserError:
        return {}
    except ValidationError:
        return {}
