"""# Demo DAGs

The demo DAGs that generate from template config file.
"""

from airflow.utils.dates import days_ago

from dagtool import DagTool

from .utils import CustomTask, say_hi

tool = DagTool(
    name="demo",
    path=__file__,
    docs=__doc__,
    user_defined_macros={"custom_macros": "foo"},
    tasks={"demo_task": CustomTask},
    python_callers={"say_hi": say_hi},
)
tool.build_airflow_dags_to_globals(
    gb=globals(),
    default_args={"start_date": days_ago(2)},
)
