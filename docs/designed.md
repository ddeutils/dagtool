# Designed

A designed document of this project.

## DAG File Structure:

I start design folder structure base on these objectives:

- Easy to maintain and develop
- Grouping business logic together
- Dynamic deploy with different environment

**The Core Components**:

1. DAG Factory Code will store at `__init__.py`
2. DAG template will store at `dag-{ name }.yml`
3. Business logic store in assets store of each DAG at `assets/`
4. Dynamic environment and resource variables will store at `variables.yml`

### Type 01: Standalone DAG

```text
dags/
├── { domain }/
│     ├── { module-dags }/
│     │     ├── __init__.py                             <--- ⚙️ DAG Factory
│     │     ├── dag.yml
│     │     ├── variables.yml
│     │     └── assets/
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
│     │     ├── dag-{ name-1 }.yml
│     │     ├── dag-{ name-2 }.yml
│     │     ├── variables.yml
│     │     └── assets/
│     │         ├── dag-{ name-1 }-schema-mapping.json
│     │         ├── dag-{ name-1 }-transform-query.sql
│     │         ├── dag-{ name-2 }-schema-mapping.json
│     │         └── dag-{ name-2 }-transform-query.sql
│     │
│     └── { module-dags }/
│           ├── __init__.py
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
