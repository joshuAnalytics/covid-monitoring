from datetime import date, timedelta
import os
import glob
from urllib.error import HTTPError

import wget
import pandas as pd
import altair as alt
import streamlit as st
from covid_monitoring.abs_csse import AbsCsse


class Regional(AbsCsse):
    """
    regional time series data from csse
    """

    def __init__(self):
        self.data_path = "_data/daily/"
        self.top_n_regions = []
        # self.df_filtered = pd.DataFrame()

    def get_data(self):
        """
        get the daily csse reports and save locally
        """
        for days_delta in range(1, 140):
            date_delta = date.today() - timedelta(days=days_delta)
            date_delta = date_delta.strftime("%m-%d-%Y")
            url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_delta}.csv"
            _, filename = os.path.split(url)
            if not os.path.exists(self.data_path + filename):
                try:
                    wget.download(url, self.data_path)
                except HTTPError:
                    st.warning(f"could not retrieve data for {date_delta}")
                    pass

    def load_csvs(self):
        """
        load the csv files and filter using some params
        """
        df = pd.concat(
            [pd.read_csv(f) for f in glob.glob(self.data_path + "*.csv")],
            ignore_index=True,
        )
        usecols = [
            "Province_State",
            "Country_Region",
            "Last_Update",
            "Confirmed",
            "Deaths",
            "Recovered",
            "Active",
            "Combined_Key",
            "Incidence_Rate",
            "Case-Fatality_Ratio",
        ]
        df = df.loc[:, usecols]
        return df

    def preprocess_data(self, df, country, region_of_interest, n, y_val):
        """
        filter using user params
        """
        self.y_val = y_val
        df = df.loc[df["Country_Region"] == country].copy()
        df["date"] = pd.to_datetime(df["Last_Update"]).dt.date
        df.dropna(subset=["date", "Province_State"], inplace=True)
        df = df.loc[df["Province_State"] != "Unknown"]

        # filter n most active regions
        max_date = df["date"].max()
        df_current_day = df.loc[df["date"] == max_date].sort_values(
            by=y_val, ascending=False
        )
        top_n_regions = list(df_current_day["Combined_Key"].head(n).values)
        if region_of_interest not in top_n_regions:
            top_n_regions.append(region_of_interest)

        df = df[df["Combined_Key"].isin(top_n_regions)]
        return df

    def plot_data(self, df, weeks_to_display):
        """
        use altair to plot csse time series
        """
        df = df[["date", "Province_State", self.y_val]].sort_values(
            by=["Province_State", "date"]
        )
        start_date = date.today() - timedelta(weeks=weeks_to_display)
        # start_date = start_date.strftime("%Y-%m-%d")
        plot = df.loc[df["date"] > start_date]
        plot["date"] = plot["date"].astype(str)
        # The basic line
        line = (
            alt.Chart(plot)
            .mark_line(interpolate="basis")
            .encode(x="date:T", y=f"{self.y_val}:Q", color="Province_State:N")
        )
        # Put the layers into a chart and bind the data
        chart = alt.layer(line).properties(width=600, height=500)
        return chart
