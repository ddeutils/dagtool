"""# Demo DAGs

The demo DAGs
"""

import logging

# WARNING: The following import is here so Airflow parses this file. It follows
#   rule of `dag_discovery_safe_mode`.
# from airflow import DAG
from dagtool import DagTool
from dagtool.plugins.templates import PLUGINS_FILTERS

logger = logging.getLogger("dagtool.dag.demo")


tool = DagTool(
    name="demo",
    path=__file__,
    docs=__doc__,
    user_defined_filters=PLUGINS_FILTERS,
)
tool.build_to_globals(
    gb=globals(),
    default_args={},
)
