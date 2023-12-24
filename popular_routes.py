import pandas as pd
from datetime import datetime, timedelta
import folium
from map_routers_roads import ROUTER_GEOM
from loguru import logger


def preprocess_wifi_data(data):
    logger.info("Preprocessing wifi_logs data..")
    data = data.drop("router_mac", axis=1)
    data["tm"] = pd.to_datetime(
        data["tm"], errors="coerce", format="%Y-%m-%d %H:%M:%S%z"
    )
    data["10_min"] = data["tm"].dt.floor("10T").dt.strftime("%H:%M")
    return data


def prepare_data(wifi_logs):
    logger.info("Preparing wifi_logs data..")
    wifi_logs = preprocess_wifi_data(wifi_logs)
    wifi_logs["1_min"] = wifi_logs["tm"].dt.floor("1T").dt.time
    logger.info("Spliting info day parts..")
    morning_mask = (wifi_logs["1_min"] >= pd.to_datetime("7:00").time()) & (
        wifi_logs["1_min"] < pd.to_datetime("9:00").time()
    )
    afternoon_mask = (wifi_logs["1_min"] >= pd.to_datetime("12:00").time()) & (
        wifi_logs["1_min"] < pd.to_datetime("17:00").time()
    )
    evening_mask = (wifi_logs["1_min"] >= pd.to_datetime("17:00").time()) & (
        wifi_logs["1_min"] < pd.to_datetime("19:00").time()
    )

    morning = wifi_logs[morning_mask]
    afternoon = wifi_logs[afternoon_mask]
    evening = wifi_logs[evening_mask]

    return morning, afternoon, evening


def transform_into_coordinates(substitute_list, existing_dict):
    logger.info("Transform into coordinates..")
    for i, key_tuple in enumerate(substitute_list):
        substitute_values = [existing_dict[key] for key in key_tuple]
        substitute_list[i] = substitute_values

    return substitute_list


def generate_routes(data):
    logger.info("Generating routes..")
    filtered_users = data.groupby("user_mac")["router_id"].nunique() > 5
    selected_users = filtered_users[filtered_users].index.tolist()
    data = data[data["user_mac"].isin(selected_users)]

    data = data.loc[data.groupby(["user_mac", "1_min"])["signal"].idxmax()][
        ["1_min", "router_id", "signal", "user_mac"]
    ]

    routes = pd.DataFrame(data.groupby("user_mac")["router_id"].unique())
    routes = routes.reset_index()

    lists = [i.tolist() for i in routes["router_id"]]

    popular_patterns = lists

    coordinates_list = transform_into_coordinates(popular_patterns, ROUTER_GEOM)

    return coordinates_list


def add_layer(fg, data, color):
    logger.info("Adding folium layers..")
    routes = generate_routes(data)
    for pattern in routes:
        for point in pattern:
            folium.Circle(
                location=point,
                color=color,
                radius=150,
                fill=True,
                fill_opacity=0.01,
                opacity=1 / 1000000,
            ).add_to(fg)


def create_map_day(data):
    morning, afternoon, evening = prepare_data(data)
    logger.info("Setting up a random point, just to open a map in Tula city")
    map_object = folium.Map(location=(54.18133, 37.604794), zoom_start=15)

    morning_fg = folium.FeatureGroup(name="Morning", show=True).add_to(map_object)
    afternoon_fg = folium.FeatureGroup(name="Afternoon", show=True).add_to(map_object)
    evening_fg = folium.FeatureGroup(name="Evening", show=True).add_to(map_object)

    add_layer(morning_fg, morning, "blue")
    add_layer(afternoon_fg, afternoon, "red")
    add_layer(evening_fg, evening, "green")

    folium.LayerControl().add_to(map_object)

    map_object.save("reports/map_with_points_day_legend_powered.html")

    return map_object


def create_map_week(data):
    data = preprocess_wifi_data(data)
    data["1_min"] = data["tm"].dt.floor("1T").dt.time

    data["is_weekday"] = data["tm"].dt.weekday < 5

    weekdays = data[data["is_weekday"] == True]
    weekends = data[data["is_weekday"] == False]
    logger.info("Setting up a random point, just to open a map in Tula city")
    map_object = folium.Map(location=(54.18133, 37.604794), zoom_start=15)

    weekdays_routes = generate_routes(weekdays)
    weekends_routes = generate_routes(weekends)

    weekdays_fg = folium.FeatureGroup(name="Weekdays", show=True).add_to(map_object)
    weekends_fg = folium.FeatureGroup(name="Weekends", show=True).add_to(map_object)

    add_layer(weekdays_fg, weekdays_routes, "blue")
    add_layer(weekends_fg, weekends_routes, "green")

    folium.LayerControl().add_to(map_object)

    map_object.save("reports/map_with_points_week_legend_powered.html")

    return map_object
