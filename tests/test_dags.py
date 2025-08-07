from airflow.decorators import dag


def test_create_dag():
    @dag(
        dag_id="demo",
    )
    def mock_create_dag():
        pass

    mock_create_dag()
