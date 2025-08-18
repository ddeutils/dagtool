"""# Stock DAGs

This is the stock domain DAG.

"""

import logging
from itertools import chain

from dedag import DeDag

logger = logging.getLogger("dedag.dag.stock")


dag = DeDag(
    name="stock",
    path=__file__,
    docs=__doc__,
    user_defined_filters={
        "unnested_list": lambda x: (
            list(chain.from_iterable(x)) if x != [] else ["no_back_fill_blob"]
        )
    },
    user_defined_macros={},
)
logger.info(f"Start Generate: {dag.name}")
dag.build_to_globals(
    gb=globals(),
    default_args={},
)
