"""# Store

This is the store domain dag

"""

import logging

from dedag import DeDag

logger = logging.getLogger("dedag.dag.store")


dag = DeDag(name="store", path=__file__, gb=globals())
logger.info(f"Start Generate: {dag.name}")
dag.gen()
