from airflow.models import DAG

with DAG(
    dag_id="pure_01_start",
    tags=["origin"],
) as dag:
    print("start origin dag")
