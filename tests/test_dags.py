from airflow import DAG
from airflow.decorators import dag


def test_create_dag_decorator():
    @dag(
        dag_id="demo",
    )
    def mock_create_dag():
        pass

    d = mock_create_dag()
    print(d)


def test_create_dag():
    d = DAG("demo")
    print(d)
