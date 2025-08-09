# Designed

## DAG File Structure:

Objective:

- Easy to maintain and develop
- Grouping business logic together
- Dynamic deploy with different environment

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
│     │     ├── dag-case-1.yml
│     │     ├── dag-case-2.yml
│     │     ├── variables.yml
│     │     └── assets/
│     │         ├── dag-case-1-schema-mapping.json
│     │         ├── dag-case-1-transform-query.sql
│     │         ├── dag-case-2-schema-mapping.json
│     │         └── dag-case-2-transform-query.sql
│     │
│     └── { module-dags }/
│           ├── __init__.py
```

The DAG name will generate with:

```text
{module-dags}-case-1
{module-dags}-case-2
```
