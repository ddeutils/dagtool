# DagTool

A **Friendly Airflow DAG Generator** for Data Engineer with YAML Template.

**Execution Flow**:

The flow of this project provide the interface Pydantic Model before
passing it to Airflow objects.

```text
S --> Template --> Pydantic Model --> DAG/Operator Objects --> Execute --> E
```
