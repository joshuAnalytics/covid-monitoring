import streamlit as st
from covid_monitoring import csse

r = csse.Regional()

st.title("virus watch ")

# load and process data

r.get_data()
r.load_csvs()


# user input parameters
y_vals = ["Incidence_Rate", "Confirmed", "Case-Fatality_Ratio", "Deaths"]
r.country = st.sidebar.selectbox("Select country", r.get_country_list(), 9)


r.region_of_interest = st.sidebar.selectbox(
    "Select region of interest", r.get_region_list(), 4
)
r.weeks_to_display = st.sidebar.slider("Number of weeks", 1, r.n_weeks_data, value=5)
r.y_val = st.sidebar.radio("Metric", y_vals, 1)
r.top_n_regions = st.sidebar.selectbox(
    "Num regions to compare", list(range(0, r.get_num_regions())), 5
)

# preprocess, passing all the user inputs as self.attributes
r.preprocess_data()

# main page
st.markdown("### regional case rates")
st.markdown("  \n  \n  \n  \n")
st.altair_chart(r.plot_data())
st.write(
    f"Displaying top {r.top_n_regions} regions compared to {r.region_of_interest} "
)


# st.markdown("### regional daily numbers")

