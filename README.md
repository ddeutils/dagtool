# DeDAG

DeDAG is friendly Airflow DAG generator for Data Engineer.

> [!WARNING]
> This project will reference the DAG generate code from the [Astronomer: DAG-Factory](https://github.com/astronomer/dag-factory).
> But I replace some logic that fit with ETL propose for Data Engineer.

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
│     │         ├── dag-schema-mapping.json
│     │         └── dag-transform-query.sql
│     │
│     └── { module-dags }/
│           ├── __init__.py
```

> [!NOTE]
> I think this project should support project structure like:
>
> ```text
> dags/
> ├── { domain }/
> │     ├── { module-dags }/
> │     │     ├── __init__.py
> │     │     ├── dag-case-1.yml
> │     │     ├── dag-case-2.yml
> │     │     ├── variables.yml
> │     │     └── assets/
> │     │         ├── dag-case-1-schema-mapping.json
> │     │         ├── dag-case-1-transform-query.sql
> │     │         ├── dag-case-2-schema-mapping.json
> │     │         └── dag-case-2-transform-query.sql
> │     │
> │     └── { module-dags }/
> │           ├── __init__.py
> ```

**Feature Supported**:

- Passing environment variable.
- Allow Passing Airflow Template.

## 📦 Installation

| Airflow Version | Supported | Noted |
|:---------------:|:---------:|-------|
|     `2.7.1`     |    :x:    |       |
|    `>=3.x.x`    |    :x:    |       |

## 🎯 Usage

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
from dedag import DokDag

doc: str = """
# SALES DAG

This DAG will extract data from Google Cloud Storage to Google BigQuery LakeHouse
via DuckDB engine.
"""

dag = DokDag(
    "sales_dag", path=__file__, gb=globals()
)
dag.gen()
```

## 💬 Contribute

I do not think this project will go around the world because it has specific propose,
and you can create by your coding without this project dependency for long term
solution. So, on this time, you can open [the GitHub issue on this project :raised_hands:](https://github.com/ddeutils/dedag/issues)
for fix bug or request new feature if you want it.
