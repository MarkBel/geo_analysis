import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from loguru import logger

import os

from popular_routes import prepare_data, create_map_day, create_map_week

import streamlit.components.v1 as components

from route_calculator import calculate_mean_time


@st.cache_data
def read_catched_data():
    wifi_logs = pd.read_csv("data/wifi_logs_2022_12_01_202312081829.csv", sep=";")
    return wifi_logs


def main():
    st.title("Wifi routers EDA by Gini team")
    data = read_catched_data()
    map_day_object = create_map_day(data)
    st.write("Popular routes during the day")
    html_day_capacity = open("reports/map_with_points_day_legend_powered.html")
    components.html(html_day_capacity.read())

    morning, afternoon, evening = prepare_data(data)
    st.dataframe(morning)

    with st.expander("Show average routes calculators"):
        morning_df = calculate_mean_time(morning)
        afternoon_df = calculate_mean_time(afternoon)
        evening_df = calculate_mean_time(evening)
        st.write("Average time for morning routes")
        st.dataframe(morning_df)
        st.write("Average time for afternoon routes")
        st.dataframe(afternoon_df)
        st.write("Average time for evening routes")
        st.dataframe(evening_df)

    st_data_day = st_folium(map_day_object, width=1500)


if __name__ == "__main__":
    main()
