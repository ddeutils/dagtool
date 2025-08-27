import os
from pathlib import Path

from airflow.models import DAG

from dagtool.factory import Factory


def test_factory(test_path: Path):
    factory = Factory("sales_dag", path=test_path / "demo")
    print(factory)
    print(factory.conf)


def test_factory_build(test_path: Path):
    factory = Factory(
        name="demo", path=test_path.parent / "dags/demo/__init__.py"
    )
    dags: list[DAG] = factory.build()
    print(dags)


def test_factory_build_to_globals(test_path: Path):
    factory = Factory(
        name="demo",
        docs="# Demo DAGS\n\nThe demo DAGS\n",
        path=test_path.parent / "dags/demo/__init__.py",
        user_defined_macros={"env": os.getenv},
    )
    factory.build_airflow_dags_to_globals(
        gb=globals(),
        default_args={"start_date": "2025-01-01 00:00:00"},
    )
    dag: DAG = globals().get("demo_03_template")
    print(dag)
    print(dag.doc_md)
