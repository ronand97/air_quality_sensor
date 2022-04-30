import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd

import utils
import simulate_dat

load_dotenv()
ENVIRONMENT = os.environ['ENVIRONMENT']


class Dashboard:
    def __init__(self) -> None:
        self.df = pd.DataFrame()

    def _get_data(self) -> None:
        """
        Get sensor reading data into pandas dataframe.
        """
        data = simulate_dat.generate_toy_data(10)
        self.df =  pd.DataFrame(data)

    def _process_data(self) -> None:
        pass

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
        self._get_data()
        self._construct_dashboard_elements()

if __name__ == "__main__":
    Dashboard().run()


