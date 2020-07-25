import streamlit as st
from covid_monitoring.csse_countries import CsseTimeSeries
from covid_monitoring.csse import Regional

st.title("holiday watch ")

# user input parameters
population_dict = {
    "Spain": 46.94,
    "United Kingdom": 66.65,
    "France": 66.99,
}
countries = population_dict.keys()
y_vals = ["Incidence_Rate", "Confirmed", "Case-Fatality_Ratio", "Deaths"]
country = st.sidebar.selectbox("Select Country", list(population_dict.keys()), 0)
weeks_to_display = st.sidebar.slider("Number of weeks", 1, 8, value=5)
y_val = st.sidebar.radio("Metric", y_vals, 1)

# load and process data
r = Regional()
df = r.load_csvs()
df = r.preprocess_data(
    df, country=country, n=5, region_of_interest="C. Valenciana, Spain", y_val=y_val
)

# cs = CsseTimeSeries()
# cs.preprocess_csse(population_dict)

# main page
st.markdown("### regional case rates")
st.markdown("  \n  \n  \n  \n")
st.altair_chart(r.plot_data(df, weeks_to_display=weeks_to_display))

# st.altair_chart(
#     r.plot_data(r.df_filtered, y_val=y_val, weeks_to_display=weeks_to_display)
# )

st.markdown("### country case rates")
