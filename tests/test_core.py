from pathlib import Path

from fastdag import FastDag


def test_fastdag(test_path: Path):
    dag = FastDag("sales_dag", path=test_path / "demo")
    print(dag)

    assert dag.dag_count == 1
    print(dag.conf)


def test_fastdag_gen(test_path: Path):
    dag = FastDag("sales_dag", path=test_path / "demo")
    print(dag.gen())

    print(globals())
