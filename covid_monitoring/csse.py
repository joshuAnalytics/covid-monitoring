from datetime import date, timedelta, datetime
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
        self.top_n_regions = None
        self.n_weeks_data = 8
        self.weeks_to_display = None
        self.region_of_interest = None
        self.df_raw = None
        self.df_processed = None
        self.country = None
        self.country_list = None
        self.region_list = None

    def get_data(self):
        """
        get the daily csse reports and save locally
        """
        for days_delta in range(1, self.n_weeks_data * 7):
            date_delta = date.today() - timedelta(days=days_delta)
            date_delta = date_delta.strftime("%m-%d-%Y")
            url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_delta}.csv"
            _, filename = os.path.split(url)
            if not os.path.exists(self.data_path + filename):
                print(filename, "doesn't exist")
                try:
                    wget.download(url, self.data_path)
                except HTTPError:
                    st.warning(f"could not retrieve data for {date_delta}")
                    pass

    def load_csvs(self):
        """
        load the csv files and filter using some params
        """
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
        df_list = []
        for f in glob.glob(self.data_path + "*.csv"):
            _, filename = os.path.split(f)
            # filename as date variable
            date_str = filename.strip(".csv")
            date_obj = datetime.strptime(date_str, "%m-%d-%Y").date()
            try:
                df = pd.read_csv(f, usecols=usecols)
                df["date"] = date_obj
                df_list.append(df)
            except:
                st.warning(f"missing columns in {filename}")

        df = pd.concat(df_list)

        # filter null regions
        null_regions = []
        for country in df["Country_Region"].unique():
            num_regions = len(
                df[df["Country_Region"] == country]["Province_State"].unique()
            )
            if num_regions < 2:
                null_regions.append(country)

        df = df.loc[~df["Country_Region"].isin(null_regions)].copy()

        self.df_raw = df
        return self.df_raw

    def get_num_regions(self):
        """
        filter the raw df by country
        """
        df = self.df_raw.copy()
        return df.loc[df["Country_Region"] == self.country, "Province_State"].nunique()

    def get_country_list(self):
        """
        return a list of all available countries
        """
        self.country_list = self.df_raw["Country_Region"].unique().tolist()
        return self.country_list

    def get_region_list(self):
        """
        return a list of regions in the selected country
        """
        if self.country is None:
            st.warning("select a country first")
        df = self.df_raw.copy()
        self.region_list = (
            df.loc[df["Country_Region"] == self.country, "Province_State"]
            .unique()
            .tolist()
        )
        return self.region_list

    def preprocess_data(self):
        """
        filter using user params
        """
        df = self.df_raw.copy()
        df = df.loc[df["Country_Region"] == self.country].copy()
        df["date"] = pd.to_datetime(df["Last_Update"]).dt.date
        df.dropna(subset=["date", "Province_State"], inplace=True)
        df = df.loc[df["Province_State"] != "Unknown"]

        # filter n most active regions
        max_date = df["date"].max()
        df_current_day = df.loc[df["date"] == max_date].sort_values(
            by=self.y_val, ascending=False
        )
        top_n_regions = list(
            df_current_day["Province_State"].head(self.top_n_regions).values
        )
        if self.region_of_interest not in top_n_regions:
            top_n_regions.append(self.region_of_interest)

        self.df_processed = df[df["Province_State"].isin(top_n_regions)]
        return self.df_processed

    def plot_data(self):
        """
        use altair to plot csse time series
        """
        if self.df_processed is None:
            st.warning("data not ready to plot")

        df = self.df_processed.copy()
        df = df[["date", "Province_State", self.y_val]].sort_values(
            by=["Province_State", "date"]
        )
        start_date = date.today() - timedelta(weeks=self.weeks_to_display)
        # start_date = start_date.strftime("%Y-%m-%d")
        plot = df.loc[df["date"] > start_date]
        plot["date"] = plot["date"].astype(str)
        # The basic line
        line = (
            alt.Chart(plot)
            .mark_line(interpolate="basis", size=2.5, opacity=0.75)
            .encode(
                x="date:T",
                y=f"{self.y_val}:Q",
                color=alt.Color(
                    "Province_State",
                    scale=alt.Scale(scheme="tableau10"),
                    legend=alt.Legend(
                        title=f"regions",
                        orient="right",
                        symbolType="stroke",
                        symbolStrokeWidth=8.5,
                    ),
                ),
            )
        )
        # Put the layers into a chart and bind the data
        chart = (
            alt.layer(line)
            .properties(width=600, height=550)
            .configure(background="#313236")
            .configure_axis(
                grid=True,
                gridWidth=0.2,
                labelColor="white",
                tickColor="grey",
                titleColor="white",
            )
            .configure_text(color="#FFFFFF")
            .configure_legend(titleColor="white", labelColor="white")
            .configure_text(color="#FFFFFF")
        )
        return chart
