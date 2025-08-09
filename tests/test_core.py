"""Test Doc"""

from pathlib import Path

from dedag import DokDag

doc: str = """
# Test DAG

This is a testing DAG.
"""


def test_dokdag(test_path: Path):
    dag = DokDag("test_dag", path=test_path, gb=globals())
    print(dag)
