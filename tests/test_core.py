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
    )
    tool.build_airflow_dags_to_globals(gb=globals())
    dag: DAG = globals().get("demo_01_start")
    print(dag)
    print(dag.get_doc_md(dag.doc_md))
