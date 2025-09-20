from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent

import click
from airflow.configuration import conf

# Import version from auto-generated file (managed by hatch + VCS)
try:
    from ._version import __version__
except ImportError:
    # Fallback for development environments without proper build
    from . import __version__


@click.group()
def cli() -> None:
    """Main DAG Gen CLI."""


@cli.command("version")
def version() -> None:
    """Return the current version of this DAG Gen package."""
    click.echo(__version__)
    sys.exit(0)


@cli.command("sync-vars")
@click.option(
    "--dags-folder",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
    help="A DAGs folder.",
)
def sync_airflow_variable(dags_folder: Path | None = None):
    """Sync Airflow Variable that already set on the DAG folder with template
    DAG Tool.
    """
    click.echo("Sync Airflow Variable does not implement yet.")
    click.echo(
        dedent(
            """
            Steps:
            - Search Variable files reference the `.airflowignore` pattern.
            - Prepare variable with prefix name.
            - Sync to the target Airflow Variable.
            """.strip(
                "\n"
            )
        )
    )
    click.echo("NOTE:")
    click.echo(f"DAGs Folder: {dags_folder or conf.get('core', 'dags_folder')}")
    sys.exit(1)


@cli.command("sync-files")
@click.option(
    "--dags-folder",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        path_type=Path,
    ),
    help="A DAGs folder.",
)
def sync_gcs_files(dags_folder: Path | None = None):
    click.echo("Sync Files to GCS does not implement yet.")
    click.echo(
        dedent(
            """
            Steps:
            - Search Sync files reference the `.airflowignore` pattern.
            - Prepare files with prefix name.
            - Sync to the target GCS.
            """.strip(
                "\n"
            )
        )
    )
    click.echo("NOTE:")
    click.echo(f"DAGs Folder: {dags_folder or conf.get('core', 'dags_folder')}")
    sys.exit(1)


@cli.command("render")
@click.option(
    "--path",
)
@click.option(
    "--name",
)
def render(name: str, path: Path):
    """Render DAG template with a specific name and path arguments to the
    Factory object.
    """
    click.echo("NOTE:")
    click.echo(f"- Name: {name}")
    click.echo(f"- Path: {path}")
    sys.exit(1)


@cli.command("validate")
@click.option(
    "--value",
)
def validate(value: str):
    """Validate DAG template with a specific name and path arguments to the
    Factory object.
    """
    click.echo("NOTE:")
    click.echo(f"- Value: {value}")
    sys.exit(1)


@cli.command("json-schema")
@click.option(
    "--file",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=Path,
    ),
    help="A JSON schema file path that want to save.",
)
def build_json_schema(file: Path | None):
    """Build JSON Schema file from the current Dag model."""
    from dagtool.models.dag import Dag

    click.echo("Start generate JSON Schema file for DAG Template.")
    Dag.build_json_schema(filepath=file or Path("./json-schema.json"))
    sys.exit(0)


if __name__ == "__main__":
    cli()
