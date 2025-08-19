"""# Stock DAGs

This is the stock domain DAG.
"""

import logging

from fastdag import FastDag
from fastdag.plugins.templates.filters import unnested_list

logger = logging.getLogger("fastdag.dag.stock")


dag = FastDag(
    name="stock",
    path=__file__,
    docs=__doc__,
    operators={},
    user_defined_filters={"unnested_list": unnested_list},
    user_defined_macros={},
)
logger.info(f"Start Generate: {dag.name}")
dag.build_to_globals(
    gb=globals(),
    default_args={},
)
