"""# Demo DAGs

The demo DAGs
"""

import logging

from airflow.utils.dates import days_ago

from dagtool import DagTool
from dagtool.plugins.templates import PLUGINS_FILTERS

logger = logging.getLogger("dagtool.dag.demo")


tool = DagTool(
    name="demo",
    path=__file__,
    docs=__doc__,
    user_defined_filters=PLUGINS_FILTERS,
)
tool.build_airflow_dags_to_globals(
    gb=globals(),
    default_args={"start_date": days_ago(2)},
)
