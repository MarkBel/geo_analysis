import pandas as pd
from difflib import SequenceMatcher
import folium
from map_routers_roads import ROUTER_GEOM


def find_common_pattern(lists):
    patterns = set()

    for i in range(len(lists)):
        for j in range(i + 1, len(lists)):
            matcher = SequenceMatcher(None, lists[i], lists[j])
            match = matcher.find_longest_match(0, len(lists[i]), 0, len(lists[j]))

            if match.size > 3:  # Minimum length of the common pattern
                common_pattern = lists[i][match.a : match.a + match.size]
                patterns.add(tuple(common_pattern))

    return patterns


def transform_into_coordinates(substitute_list, existing_dict):
    for i, key_tuple in enumerate(substitute_list):
        substitute_values = [existing_dict[key] for key in key_tuple]
        substitute_list[i] = substitute_values

    return substitute_list


def calculate_similarity(list1, list2):
    matcher = SequenceMatcher(None, list1, list2)
    similarity_percentage = matcher.ratio()
    return similarity_percentage


def find_pattern(value, patterns):
    similarity = 0
    best_pattern = 0
    for pattern in patterns:
        if calculate_similarity(value, pattern) > similarity:
            similarity = calculate_similarity(value, pattern)
            best_pattern = pattern
    return best_pattern


def prepare_data(path):
    wifi_logs = pd.read_csv(path, sep=";")
    wifi_logs["tm"] = pd.to_datetime(wifi_logs["tm"])
    wifi_logs["1_min"] = wifi_logs["tm"].dt.floor("1T").dt.strftime("%H:%M")
    morning = wifi_logs[
        (pd.to_datetime(wifi_logs["1_min"]) < pd.to_datetime("9:00"))
        & (pd.to_datetime("7:00") < pd.to_datetime(wifi_logs["1_min"]))
    ]
    afternoon = wifi_logs[
        (pd.to_datetime(wifi_logs["1_min"]) < pd.to_datetime("15:00"))
        & (pd.to_datetime("12:00") < pd.to_datetime(wifi_logs["1_min"]))
    ]
    evening = wifi_logs[
        (pd.to_datetime(wifi_logs["1_min"]) < pd.to_datetime("20:00"))
        & (pd.to_datetime("17:00") < pd.to_datetime(wifi_logs["1_min"]))
    ]

    return morning, afternoon, evening


def create_maps(data):

    filtered_users = data.groupby("user_mac")["router_id"].nunique() > 5
    selected_users = filtered_users[filtered_users].index.tolist()
    data = data[data["user_mac"].isin(selected_users)]

    data = data.loc[data.groupby(["user_mac", "1_min"])["signal"].idxmax()][
        ["1_min", "router_id", "signal", "user_mac"]
    ]

    routes = pd.DataFrame(data.groupby("user_mac")["router_id"].unique())
    routes = routes.reset_index()

    lists = [i.tolist() for i in routes["router_id"]]

    common_patterns = find_common_pattern(lists)
    common_patterns = [list(i) for i in common_patterns]

    found_patterns = []
    for i in routes["router_id"]:
        found_patterns.append(find_pattern(i, common_patterns))

    routes["patterns"] = pd.Series(found_patterns)

    pattern_counts = routes["patterns"].value_counts()
    popular_patterns = pattern_counts[pattern_counts >= 3].index.tolist()
    popular_patterns = [list(i) for i in popular_patterns]

    coordinates_list = transform_into_coordinates(popular_patterns, ROUTER_GEOM)
    map_objects_list: list = []
    for i, route in enumerate(coordinates_list):
        map_object = folium.Map(location=coordinates_list[0][0], zoom_start=15)
        for point in route:
            folium.Marker(location=point, popup=point, icon=folium.Icon("blue")).add_to(
                map_object
            )
        map_objects_list.append(map_object)
        # map_object.save('map_with_points_afternoon_' + str(i) + '.html')

    return map_objects_list
