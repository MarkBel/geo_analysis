import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from loguru import logger

logger.debug("Loguru geo app logging init..")


def main():
    st.write("Loguru geo app")
    wifi_routers = pd.read_csv("data/wifi_routers.csv", sep=";")
    road_network = pd.read_csv("data/road_network.csv", sep=";")
    road_network = road_network.dropna()

    def extract_points(points):
        lat = float(points.split()[1][1:])
        lan = float(points.split()[2][:-1])
        return lan, lat

    def extract_roads(roads):
        roads = roads.split(",")
        c1 = extract_points(roads[0])
        c2 = [float(i) for i in roads[1].split()]
        c2 = tuple([c2[1], c2[0]])
        c3 = roads[2].split()
        c3_1 = c3[1][:-1]
        c3 = tuple([float(c3_1), float(c3[0])])
        return c1, c2, c3

    def satisfies_condition(tuple_value):
        c1, c2 = tuple_value
        return 54.1500 < c1 < 54.2700 and 37.5600 < c2 < 37.6800

    routers = wifi_routers["geom"].apply(extract_points)
    roads = road_network["geom"].apply(extract_roads)
    roads = [
        tuple_group
        for tuple_group in roads
        if all(satisfies_condition(inner_tuple) for inner_tuple in tuple_group)
    ]

    map_object = folium.Map(location=routers[1], zoom_start=50)

    for point in routers:
        folium.Marker(location=point, popup=point).add_to(map_object)

    for road in roads:
        folium.PolyLine(locations=road, color="blue").add_to(map_object)

    # left, right = st.columns(2)
    # st_data = st_folium(map_object, width=1500)

    # with left:
    #     st.write("Folium labeled map")
    #
    #
    # with right:
    #     st.write("Description")


if __name__ == "__main__":
    main()
