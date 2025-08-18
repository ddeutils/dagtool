"""# Stock DAGs

This is the stock domain DAG.
"""

import logging

from dedag import DeDag
from dedag.plugins.templates.filters import unnested_list

logger = logging.getLogger("dedag.dag.stock")


dag = DeDag(
    name="stock",
    path=__file__,
    docs=__doc__,
    user_defined_filters={"unnested_list": unnested_list},
    user_defined_macros={},
)
logger.info(f"Start Generate: {dag.name}")
dag.build_to_globals(
    gb=globals(),
    default_args={},
)
