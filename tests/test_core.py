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


def test_dagtool_gen_dags(test_path: Path):
    tool = DagTool(
        name="demo",
        path=test_path.parent / "dags/demo/__init__.py",
    )
    tool.build_to_globals(gb=globals())
    dag = globals().get("demo_01_start")
    print(dag)
