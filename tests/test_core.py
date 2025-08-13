"""Test Doc"""

from pathlib import Path

from dedag import DeDag

doc: str = """
# Test DAG

This is a testing DAG.
"""


def test_dokdag(test_path: Path):
    dag = DeDag("test_dag", path=test_path, gb=globals())
    print(dag)
