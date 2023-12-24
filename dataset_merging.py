import os
import plotly.express as px
import pandas as pd


def merge_month_like_and_render_figure():
    # загрузка данных о роутерах
    wifi_routers = pd.read_csv("data/wifi_routers_clusters.csv", sep=";")

    # Можно скачать папку с яндекса
    folder_path = "wifi_logs_2022_12"

    wifi_logs = pd.DataFrame(
        columns=["guid", "tm", "router_mac", "user_mac", "signal", "router_id"]
    )
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        wifi_log = pd.read_csv(file_path, sep=";")
        wifi_logs = pd.concat([wifi_logs, wifi_log], axis=0)

    wifi_logs.to_parquet("wifi_logs_2022_12.parquet.gzip", compression="gzip")
    # pd.read_parquet("wifi_logs_2022_12.parquet.gzip")
    wifi_logs["tm"] = pd.to_datetime(wifi_logs["tm"])

    # 10 min срез
    wifi_logs["10_min"] = wifi_logs["tm"].dt.floor("10T").dt.strftime("%H:%M")

    # выходной/будний
    wifi_logs["is_weekday"] = wifi_logs["tm"].dt.weekday < 5
    weekdays = wifi_logs[wifi_logs["is_weekday"] == True]
    weekends = wifi_logs[wifi_logs["is_weekday"] == False]

    # соединение датасетов wifi_routers и wifi_logs по id роутера
    wifi_logs_clusters = wifi_routers.merge(
        wifi_logs, right_on="router_id", left_on="guid"
    )
    wifi_logs_clusters.drop("guid_x", axis=1, inplace=True)
    wifi_logs_clusters = wifi_logs_clusters.rename(columns={"guid_y": "guid"})

    # удалить данные об уникальных пользователях
    real_users = wifi_logs_clusters.duplicated(subset=["user_mac"], keep=False)
    wifi_logs_clusters = wifi_logs_clusters[real_users]

    ## графики
    fig = px.line(
        wifi_logs.groupby("10_min")["guid"].count(),
        title="Количество подключений в течении дня",
    )
    fig.show()

    fig = px.line(
        x=weekdays["10_min"].unique(),
        y=[
            weekdays.groupby("10_min")["guid"].count(),
            weekends.groupby("10_min")["guid"].count(),
        ],
        title="Количество подключений в будние(синий) и выходные(красный)",
    )

    fig.show()
