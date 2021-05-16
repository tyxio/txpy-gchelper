import logging
import os

import pandas as pandas

from google.cloud import bigquery


logger = logging.getLogger(__name__)

class BigQuery:

    def __init__(self, 
        client : bigquery.Client
        ):

        logger.info(f"Create Big Query client ")

        self.bq_client = client

    def bq_to_df(self,
        project_id : str,
        dataset_id : str,
        table_id : str
        ) -> pandas.DataFrame :
        """Fetches Data From BQ Dataset, outputs as dataframe."""

        try:
            table = self.bq_client.get_table(f"{project_id}.{dataset_id}.{table_id}")
            df = self.bq_client.list_rows(table).to_dataframe()
        
        except Exception: 
            logger.exception("")

        return df


