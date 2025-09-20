# Contributing

## Prerequisite

Start setup Python environment for version [`3.10`](./.python-version) and
install `dev` dependency.

A document for start contribute this package.

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

## Start Local Provisioning

The first step to make sure that your physical environment can test any feature
on the local is start running Airflow container with standalone mode.

Follow the [Build Document](./docs/build.md)

---

For starting contributed this project, it divides to 2 phases.

## Development

### Set JSON Schema

Attach JSON Schema file, `json-schema.json`, to your current IDE with file pattern
`dag*.yaml` and `dag*.yml`.

### Start develop features

> [!note]
> Install the minimum deps version;
>
> ```shell
> uv pip install "apache-airflow[google]==2.7.1" "pydantic==2.9.2"
> ```

### Wrapped with unittest

For testing, we will focus on the `tests/` folder.

## Release

### Create JSON Schema

Start checking the current CLI.

```shell
uv run --no-sync -- dagtool --help
```

```shell
uv run --no-default-groups -- dagtool json-schema
```

### Create Tag and Changelogs

### Deploy

Start deploy the new version package sync to each Airflow.
