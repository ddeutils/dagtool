from airflow.models.dagbag import DagBag


def test_dag(test_path):
    dag_bag = DagBag(dag_folder=test_path / "dags")
    print(dag_bag)
