import streamlit as st
from dotenv import load_dotenv
import os
import time
from pathlib import Path
import pandas as pd
from multiprocessing import AuthenticationError
import utils

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

class Dashboard:
    def __init__(
            self,
            cassandra_client_id: str,
            cassandra_client_secret: str,
            cassandra_config_fp: str) -> None:
        
        self.df = pd.DataFrame()

        self.cassandra_client_id = cassandra_client_id
        self.cassandra_client_secret = cassandra_client_secret
        self.cassandra_config_fp = cassandra_config_fp
        self._cassandra_auth()

    def _cassandra_auth(self) -> None:
        cloud_config= {'secure_connect_bundle': self.cassandra_config_fp}
        auth_provider = PlainTextAuthProvider(self.cassandra_client_id, self.cassandra_client_secret)
        self.cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
        self.session = self.cluster.connect("air_quality_data")
        row = self.session.execute("select release_version from system.local").one()
        if row:
            print(row[0])
        else:
            raise AuthenticationError("Failed to auth to cassandra db")

    def _get_data(self, cache_seconds: int, fp: str = "data.parquet") -> None:
        """
        Get sensor reading data. Performs simple manual caching
        by dumping to local parquet file and overwriting with latest
        data.
        """
        p = Path(fp)
        # check if file exists and use if applicable
        if p.exists():
            last_modified = os.path.getmtime(p)
            if (time.time() - last_modified) < cache_seconds:
                self.df = pd.read_parquet(p)
                return

        query_str = """
        SELECT * FROM air_quality_data.measurements
        """
        self.df = pd.DataFrame(self.session.execute(query_str).all())
        self.df.to_parquet(p)

    def _process_data(self) -> None:
        
        self.df = self.df\
            .assign(
                datetime=pd.to_datetime(self.df['timestamp'], unit='s')
                )\
            .sort_values(by='datetime', ascending=False)

    def _construct_dashboard_elements(self) -> None:
        st.set_page_config(layout="wide")
        st.title("""Air Quality Index Dashboard""")
        st.plotly_chart(
            figure_or_data=utils.create_plotly_line_chart(self.df),
            use_container_width=True)
        st.write(self.df)

    def run(self) -> None:
        """
        Main orchestration function to run dashboard. Fetches sensor
        reading data and launches streamlit dashboard.
        """
        self._get_data(cache_seconds=60*30)
        self._process_data()
        self._construct_dashboard_elements()

if __name__ == "__main__":

    load_dotenv()
    ENVIRONMENT = os.environ['ENVIRONMENT']
    CASSANDRA_CLIENT_ID = os.environ['CASSANDRA_CLIENT_ID']
    CASSANDRA_CLIENT_SECRET = os.environ['CASSANDRA_CLIENT_SECRET']
    CASSANDRA_CONFIG_FP = os.environ['CASSANDRA_CONFIG_FP']

    dashboard = Dashboard(
        cassandra_client_id=CASSANDRA_CLIENT_ID,
        cassandra_client_secret=CASSANDRA_CLIENT_SECRET,
        cassandra_config_fp=CASSANDRA_CONFIG_FP)
    dashboard.run()


