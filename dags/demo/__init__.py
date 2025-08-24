"""# Demo DAGs

The demo DAGs that generate from template config file.
"""

import logging
import os

from airflow.utils.dates import days_ago

from dagtool import DagTool

logger = logging.getLogger("dagtool.dag.demo")


tool = DagTool(
    name="demo",
    path=__file__,
    docs=__doc__,
)
tool.build_airflow_dags_to_globals(
    gb=globals(),
    default_args={"start_date": days_ago(2)},
    user_defined_macros={
        "custom_macros": "foo",
        "env": os.getenv,
    },
)
