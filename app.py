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
    logger.info("Reading wifi_logs data..")
    # Можно скачать папку с яндекса
    folder_path = "wifi_logs_2022_12_1"

    wifi_logs = pd.DataFrame(
        columns=["guid", "tm", "router_mac", "user_mac", "signal", "router_id"]
    )
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        wifi_log = pd.read_csv(file_path, sep=";")
        wifi_logs = pd.concat([wifi_logs, wifi_log], axis=0)
    return wifi_logs


def main():
    st.title("Wifi routers EDA by Gini team")
    data = read_catched_data()
    map_day_object = create_map_day(data)
    st.write("Popular routes during the day")
    html_day_capacity = open("reports/map_with_points_day_legend_powered.html")
    components.html(html_day_capacity.read())

    data_for_routes_df = read_catched_data()
    morning, afternoon, evening = prepare_data(data_for_routes_df)

    with st.expander("Show average routes calculators"):
        morning_df = calculate_mean_time(morning)
        afternoon_df = calculate_mean_time(afternoon)
        evening_df = calculate_mean_time(evening)
        st.write("Average time for morning routes")
        st.dataframe(calculate_mean_time(morning_df))
        st.write("Average time for afternoon routes")
        st.dataframe(calculate_mean_time(afternoon_df))
        st.write("Average time for evening routes")
        st.dataframe(calculate_mean_time(evening_df))

    st_data_day = st_folium(map_day_object, width=1500)


if __name__ == "__main__":
    main()
