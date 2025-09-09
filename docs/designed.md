# Designed

A designed document of this project for the production policy.

## DAG File Structure:

I start design folder structure base on these objectives:

- Easy to maintain and develop
- Grouping business logic together
- Dynamic deploy with different environment

**The Core Components**:

1. DAG Factory Code will store at `__init__.py`
2. DAG template will store at `dag_{ name }.yml`
3. Business logic store in assets store of each DAG at `assets/`
4. Dynamic environment and resource variables will store at `variables.yml`

**Other Components**:

```text
├── dags/
│   ├── pipelines/
│   │    └── { domain }/
│   ├── management/
│   └── utils/
├── tests/
```

> [!NOTE]
> - `dags/pipelines/`
>   - `dags/pipelines/domain/__init__.py`
>   - `dags/pipelines/domain/sub-domain/__init__.py`
> - `dags/managements/`
>   - `dags/management/monitor/{propose}`
>   - `dags/management/iceberg/{propose}`
>   - `dags/management/actions/{propose}`
> - `dags/utils/`
>   - `dags/utils/plugins/google/operators`
>   - `dags/utils/plugins/google/sensors`
>   - `dags/utils/plugins/common/sensors`
>   - `dags/utils/tasks/common/{propost}`
>   - `dags/utils/reusables/{propose}`
> - `plugins/callbacks`

### Type 01: Standalone DAG

```text
dags/
├── { domain }/
│     ├── { module-dags }/
│     │     ├── __init__.py                             <--- ⚙️ DAG Factory
│     │     ├── dag.yml                                 <--- DAG Template
│     │     ├── variables.yml                           <--- Variables
│     │     └── assets/                                 <--- Assets
│     │         ├── dag-schema-mapping.json
│     │         └── dag-transform-query.sql
│     │
│     └── { module-dags }/
│           ├── __init__.py
```

### Type 02: Multiple DAGs

```text
dags/
├── { domain }/
│     ├── { module-dags }/
│     │     ├── __init__.py                             <--- ⚙️ DAG Factory
│     │     ├── dag-{ name-1 }.yml                      <--- DAG Template
│     │     ├── dag-{ name-2 }.yml                      <--- DAG Template
│     │     ├── variables.yml                           <--- Variables
│     │     └── assets/                                 <--- Assets
│     │         ├── dag-{ name-1 }-schema-mapping.json
│     │         ├── dag-{ name-1 }-transform-query.sql
│     │         ├── dag-{ name-2 }-schema-mapping.json
│     │         └── dag-{ name-2 }-transform-query.sql
│     │
│     └── { module-dags }/
│           ├── __init__.py                             <--- ⚙️ DAG Factory
```

The DAG name will generate with:

```text
DAG: { module-dags }-{ name-1 }
DAG: { module-dags }-{ name-2 }
```

## Variables Sync

1. (Best Practice) Keep it on the Airflow variables
2. Keep it on Object Storage
3. Keep it on the Current DAG folder
