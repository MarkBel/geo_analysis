import pandas as pd
from datetime import datetime, timedelta
from loguru import logger

from map_routers_roads import ROUTER_GEOM
from popular_routes import prepare_data


def return_first(l):
    return l[0]


def return_last(l):
    return l[-1]


def transform_into_coordinates(substitute_list, existing_dict):
    logger.info("Transform into coordinates..")
    for i, key_tuple in enumerate(substitute_list):
        substitute_values = [existing_dict[key] for key in key_tuple]
        substitute_list[i] = substitute_values

    return substitute_list


def calculate_mean_time(data):

    data = data.loc[data.groupby(["user_mac", "1_min"])["signal"].idxmax()][
        ["1_min", "router_id", "user_mac"]
    ]

    routes = pd.DataFrame(data.groupby("user_mac")["router_id"].unique())
    routes = routes.reset_index()

    routes = routes[routes["router_id"].apply(lambda x: len(x) >= 3)]

    first_last_time = (
        data.groupby("user_mac")["1_min"].agg(["min", "max"]).reset_index()
    )

    df = pd.merge(routes, first_last_time, on="user_mac", how="left")

    df["first_router"] = df["router_id"].apply(return_first)
    df["last_router"] = df["router_id"].apply(return_last)

    df["time_spent"] = df.apply(
        lambda row: (
            datetime.combine(datetime.today(), row["max"])
            - datetime.combine(datetime.today(), row["min"])
        )
        // timedelta(minutes=1),
        axis=1,
    )

    df["first_router"] = transform_into_coordinates(
        [[i] for i in df["first_router"].tolist()], ROUTER_GEOM
    )
    df["last_router"] = transform_into_coordinates(
        [[i] for i in df["last_router"].tolist()], ROUTER_GEOM
    )

    return df[["first_router", "last_router", "time_spent"]].sort_values(
        by="time_spent", ascending=False
    )
