from pathlib import Path

from dagtool import DagTool


def test_dagtool(test_path: Path):
    dag = DagTool("sales_dag", path=test_path / "demo")
    print(dag)

    assert dag.dag_count == 1
    print(dag.conf)


def test_dagtool_gen(test_path: Path):
    dag = DagTool("sales_dag", path=test_path / "demo")
    print(dag.gen())

    print(globals())
