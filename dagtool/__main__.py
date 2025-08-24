import sys

import click

from .__about__ import __version__


@click.group()
def cli() -> None:
    """Main Tool CLI."""


@cli.command("version")
def version() -> None:
    click.echo(__version__)


@cli.command("sync-vars")
def sync_airflow_variable():
    click.echo("Sync Airflow Variable does not implement yet.")
    sys.exit(1)


if __name__ == "__main__":
    cli()
