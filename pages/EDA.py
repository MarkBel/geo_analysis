import streamlit as st
from PIL import Image
import pandas as pd

st.set_page_config(
    page_title="Geo EDA", page_icon="🧊", layout="wide", initial_sidebar_state="expanded"
)

# @st.cache_data
# def read_from_parquet():
#     return pd.read_parquet("wifi_logs_2022_12.parquet.gzip")


def app():
    with st.expander("See explanation"):
        st.write(
            """
        1. Топ популярных маршрутов за все время и затраченное на них время в разное время суток
        2. Определить час пик в разных районах города (работа с кластерами)
        3. Сравнить нагруженность центра города в праздники с будними днями
        4. Объединить роутеры в кластеры, проанализировать загруженность дорог по районам
        5. Сгрупировать все данные по дням недели (выходной/будний) и провести сравнительный анализ
        6. Самые посещаемые места (кроме дома) и другая статистика для каждого пользователя если за каждым пользователем закреплен неизменный id
        7. Определить транспортное средство
        
        
         8. Отфильтровать фрилансеров по сигналу (по идее самый стабильный сигнал будет дома)
  
        - можно сгруппировать по пользователям и определить маршруты (порядок посещения роутеров в течении дня)
        - определим самые частые маршруты, но нет инфы о скорости/средстве передвижения
        - по идее можно привязать это ко времени и определить самые частые маршруты в определенные часы
        - можно не строить точный маршрут пользователя на карте, главное понять направление и порядок посещения роутеров (?)
        - взять 1-3 наиболее активных пользователей и прикинуть среднее количество времени затраченное на один маршрут. возможно поможет с определением стартовой и конечной точки маршрута для остальных пользоваталей
     """
        )
        import os
        st.write(os.getcwd())
        st.image(Image.open("generated_pictures/visual_clusters.jpg"), width=1000)
        st.image(Image.open("generated_pictures/connections_weekday_weekend_picktime.png"), width=1000)
        st.image(Image.open("generated_pictures/connections_per_day.png"), width=1000)
    chosen = st.selectbox(
        "Pick up the aggregation range", ["weekday", "weekend"]
    )

    # st.dataframe(read_from_parquet())

if __name__=='__main__':
    app()