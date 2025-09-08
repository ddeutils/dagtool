# Contributing

## Prerequisite

Start setup Python environment for version [`3.10`](./.python-version) and
install `dev` dependency.

```shell
uv venv --python=3.10
source .venv/bin/activate
uv pip install -r pyproject.toml --extra dev
```

> [!NOTE]
> Linting and checking:
>
> ```shell
> pre-commit install
> ```

## Build Local Airflow

Follow the [building document](./docs/build.md)
