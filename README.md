# DukDig

DukDig is friendly Airflow DAG generator for Data Engineer.

This template will generate routing task.

**File Structure**:

```text
dags/
├── { domain }/
│     ├── { module-dags }/
│     │     ├── __init__.py
│     │     ├── dag.yml
│     │     ├── variables.yml
│     │     └── assets/
│     │         ├── schema-mapping.json
│     │         └── transform-query.sql
│     │
│     └── { module-dags }/
│           ├── __init__.py
```

## Installation

| Airflow Version | Supported | Noted |
|:---------------:|:---------:|-------|
|     `2.7.1`     |    :x:    |       |
|     `3.x.x`     |    :x:    |       |

## Examples

This DAG generator engine need you define the `dag.yaml` file and set engine
object to get the current path on `__init__.py` file.

> [!NOTE]
> If you want to dynamic environment config on `dag.yaml` file, you can use a
> `variable.yaml` file for dynamic value that marking on config template.

```yaml
name: sales_dag
schedule: "@daily"
authors: ["de-team"]
tasks:
  - name: start

  - name: etl_sales_master
    upstream: start
    type: group
    tasks:
      - name: extract
        type: task
        op: python
        uses: libs.gcs.csv@1.1.0
        assets:
          - name: schema-mapping.json
            alias: schema
            convertor: basic
        params:
          path: gcs://{{ var("PROJECT_ID") }}/sales/master/date/{ exec_date:%y }

      - name: transform
        upstream: extract
        type: task
        op: docker
        uses: docker.rgt.co.th/image.transform:0.0.1
        assets:
          - name: transform-query.sql
            alias: transform
        params:
          path: gcs://{{ var("PROJECT_ID") }}/landing/master/date/{ exec_date:%y }

      - name: sink
        type: task
        op: python
        run: |
          import time
          time.sleep(5)

  - name: end
    upstream: etl_sales_master
```

```python
from dukdig import DokDag

doc = """
# SALES DAG

This DAG will extract data from Google Cloud Storage to Google BigQuery LakeHouse
via DuckDB engine.
"""

dag = DokDag(
    "sales_dag", path=__file__, gb=globals()
)
dag.gen()
```
