import os
from pathlib import Path

from airflow.models import DAG

from dagtool import DagTool


def test_dagtool(test_path: Path):
    dag = DagTool("sales_dag", path=test_path / "demo")
    print(dag)

    assert dag.dag_count == 1
    print(dag.conf)


def test_dagtool_build(test_path: Path):
    tool = DagTool(name="demo", path=test_path.parent / "dags/demo/__init__.py")
    dags: list[DAG] = tool.build()
    print(dags)


def test_dagtool_build_to_globals(test_path: Path):
    tool = DagTool(
        name="demo",
        docs="# Demo DAGS\n\nThe demo DAGS\n",
        path=test_path.parent / "dags/demo/__init__.py",
        user_defined_macros={"env": os.getenv},
    )
    tool.build_airflow_dags_to_globals(
        gb=globals(),
        default_args={"start_date": "2025-01-01 00:00:00"},
    )
    dag: DAG = globals().get("demo_03_template")
    print(dag)
    print(dag.doc_md)
