# DeDAG

**Friendly Airflow DAG Generator** for Data Engineer with YAML Template.

> [!WARNING]
> This project will reference the DAG generate code from the [Astronomer: DAG-Factory](https://github.com/astronomer/dag-factory).
> But I replace some logic that fit with ETL propose for Data Engineer.

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

- JSON Schema validation
- Passing environment variable
- Allow Passing Airflow Template

## 📦 Installation

| Airflow Version | Supported | Noted |
|:---------------:|:---------:|-------|
|     `2.7.1`     |    :x:    |       |
|    `>=3.x.x`    |    :x:    |       |

## 🎯 Usage

This DAG generator engine need you define the `dag.yml` file and set engine
object to get the current path on `__init__.py` file.

> [!NOTE]
> If you want to dynamic environment config on `dag.yaml` file, you can use a
> `variable.yaml` file for dynamic value that marking on config template.

```yaml
name: sales_dag
schedule: "@daily"
authors: ["de-team"]
tags: ["sales", "tier-1", "daily"]
tasks:
  - task: start
    op: empty

  - group: etl_sales_master
    upstream: start
    tasks:
      - type: extract
        op: python
        uses: libs.gcs.csv@1.1.0
        assets:
          - name: schema-mapping.json
            alias: schema
            convertor: basic
        params:
          path: gcs://{{ var("PROJECT_ID") }}/sales/master/date/{ exec_date:%y }

      - task: transform
        upstream: extract
        op: docker
        uses: docker.rgt.co.th/image.transform:0.0.1
        assets:
          - name: transform-query.sql
            alias: transform
        params:
          path: gcs://{{ var("PROJECT_ID") }}/landing/master/date/{ exec_date:%y }

      - task: sink
        op: python
        run: |
          import time
          time.sleep(5)

  - task: end
    upstream: etl_sales_master
    op: empty
```

```python
"""# SALES DAG

This DAG will extract data from Google Cloud Storage to Google BigQuery LakeHouse
via DuckDB engine.

> This DAG is the temp DAG for ingest data to GCP.
"""
from dedag import DeDag

dag = DeDag(
    "sales_dag", path=__file__, gb=globals()
)
dag.gen()
```

## 💬 Contribute

I do not think this project will go around the world because it has specific propose,
and you can create by your coding without this project dependency for long term
solution. So, on this time, you can open [the GitHub issue on this project :raised_hands:](https://github.com/ddeutils/dedag/issues)
for fix bug or request new feature if you want it.
