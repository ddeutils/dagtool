"""Test Doc"""

from pathlib import Path

from dedag import DeDag

docs: str = """
# Test DAG

This is a testing DAG.
"""


def test_dedag(test_path: Path):
    dag = DeDag("sales_dag", path=test_path / "demo", gb=globals())
    print(dag)

    assert dag.dag_count == 1
    print(dag.conf)


def test_dedag_gen(test_path: Path):
    dag = DeDag("sales_dag", path=test_path / "demo", gb=globals())
    print(dag.gen())

    print(globals())
