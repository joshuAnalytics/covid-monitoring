from datetime import date, timedelta
import pandas as pd
import wget
import altair as alt

population = {"Spain": 46.94, "Hungary": 9.773, "United Kingdom": 66.65}


class CsseTimeSeries:
    """
    get time series data from the csse repo
    """

    def __init__(self):
        self.latest_csv = wget.download(
            "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
            "_data/",
        )
        self.df_raw = pd.read_csv(self.latest_csv)
        self.df_time_series = pd.DataFrame()

    def control_for_population(self, cases, population):
        if not cases == 0:
            pop_M = population * 10 ** 6
            control = (cases / pop_M) * 10 ** 6
            return control

    def preprocess_csse(self, population_dict, control_population=True):
        """
        clean and transpose and melt the csse data
        """
        df = self.df_raw.copy()
        meta_cols = ["Province/State", "Country/Region", "Lat", "Long"]
        time_series = df.drop(meta_cols, axis=1)
        # get a unique country name to use as id
        df["Province/State"] = df["Province/State"].fillna("")
        df["country"] = df["Country/Region"] + " " + df["Province/State"]
        df["country"] = df["country"].str.rstrip()
        # pivot the dataframe
        time_series = time_series.T
        time_series.columns = df["country"]
        # control for population
        if control_population:
            for key, val in population_dict.items():
                time_series[key] = time_series[key].apply(
                    lambda x: self.control_for_population(x, val)
                )

        # melt countries and deaths into single column
        df_melted = pd.melt(time_series.reset_index(), id_vars=["index"])
        df_melted.columns = ["date", "country", "cases per million"]
        df_melted["date"] = pd.to_datetime(df_melted["date"])
        self.df_time_series = df_melted
        return

    def plot_time_series(
        self, countries, weeks_to_display, y_label="cases per million"
    ):
        """
        use altair to plot csse time series
        """
        if self.df_time_series.empty:
            raise ("data not processed")
        df = self.df_time_series.copy()
        # filter countries
        plot = df.loc[df["country"].isin(countries)]
        # filter time window
        start_date = date.today() - timedelta(weeks=weeks_to_display)
        start_date = start_date.strftime("%Y-%m-%d")
        plot = plot.loc[plot["date"] > start_date]
        # The basic line
        line = (
            alt.Chart(plot)
            .mark_line(interpolate="basis")
            .encode(x="date:T", y=f"{y_label}:Q", color="country:N")
        )
        # Put the layers into a chart and bind the data
        chart = alt.layer(line).properties(width=600, height=500)
        return chart
