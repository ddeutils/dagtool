"""# Stock DAGs

This is the stock domain DAG.
"""

import logging

from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryGetDataOperator,
    BigQueryInsertJobOperator,
)
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator

from dagtool import DagTool
from dagtool.plugins.templates.filters import unnested_list

logger = logging.getLogger("dagtool.dag.stock")


dag = DagTool(
    name="stock",
    path=__file__,
    docs=__doc__,
    operators={
        "bigquery_insert_job_operator": BigQueryInsertJobOperator,
        "bigquery_get_data_operator": BigQueryGetDataOperator,
        "gcs_to_gcs": GCSToGCSOperator,
    },
    user_defined_filters={"unnested_list": unnested_list},
    user_defined_macros={},
)
logger.info(f"Start Generate: {dag.name}")
dag.build_to_globals(
    gb=globals(),
    default_args={},
)
