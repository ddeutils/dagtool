"""# Demo DAGs

The demo DAGs that generate from template config file.
"""

from dagtool import Factory
from dagtool.providers.common.operators.debug import DebugOperator
from dagtool.utils import days_ago

from .utils import CustomTool, say_hi

factory = Factory(
    name="demo",
    path=__file__,
    docs=__doc__,
    user_defined_macros={"custom_macros": "foo"},
    operators={"import_debug": DebugOperator},
    tools={"demo": CustomTool},
    python_callers={"say_hi": say_hi},
)
factory.build_airflow_dags_to_globals(
    gb=globals(),
    default_args={"start_date": days_ago(2)},
)
