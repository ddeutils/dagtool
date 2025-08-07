# DukDig

DukDig is friendly Airflow DAG generator for Data Engineer.

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

| Airflow Version | Supported |
|:---------------:|:---------:|
|     `3.x.x`     |    :x:    |
|     `2.x.x`     |    :x:    |

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

  - name: load_sales_master
    upstream: start
    type: group
    tasks:
      - name: extract_sales_master
        type: task
        module: load
        conn: gcs
        file_type: csv
        path: gcs://{{ var("PROJECT_ID") }}/sales/master/date/{ exec_date:%y }
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
