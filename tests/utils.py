from pathlib import Path


def make_dotenv(path: Path) -> None:
    with (path / ".env").open(mode="wt") as f:
        f.write(
            """
            AIRFLOW__CORE__UNIT_TEST_MODE=true
            AIRFLOW_ENV=dev
            """.strip(
                "\n"
            )
        )
