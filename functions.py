import pandas as pd
from datetime import datetime, timedelta


OPACITY = 1 / len(wifi_logs)


def preprocess_wifi_data(data):
  data = data.drop('router_mac', axis = 1)
  data['tm'] = pd.to_datetime(data['tm'], errors = 'coerce', format='%Y-%m-%d %H:%M:%S%z')
  data['10_min'] = data['tm'].dt.floor('10T').dt.strftime('%H:%M')

  return data

def prepare_data(wifi_logs):
    wifi_logs['1_min'] = wifi_logs['tm'].dt.floor('1T').dt.time

    morning_mask = (wifi_logs['1_min'] >= pd.to_datetime('7:00').time()) & (wifi_logs['1_min'] < pd.to_datetime('9:00').time())
    afternoon_mask = (wifi_logs['1_min'] >= pd.to_datetime('12:00').time()) & (wifi_logs['1_min'] < pd.to_datetime('17:00').time())
    evening_mask = (wifi_logs['1_min'] >= pd.to_datetime('17:00').time()) & (wifi_logs['1_min'] < pd.to_datetime('19:00').time())

    morning = wifi_logs[morning_mask]
    afternoon = wifi_logs[afternoon_mask]
    evening = wifi_logs[evening_mask]

    return morning, afternoon, evening


def transform_into_coordinates(substitute_list, existing_dict):
  for i, key_tuple in enumerate(substitute_list):
      substitute_values = [existing_dict[key] for key in key_tuple]
      substitute_list[i] = substitute_values

  return substitute_list

def generate_routes(data):
  filtered_users = data.groupby('user_mac')['router_id'].nunique() > 5
  selected_users = filtered_users[filtered_users].index.tolist()
  data = data[data['user_mac'].isin(selected_users)]

  data = data.loc[data.groupby(['user_mac', '1_min'])['signal'].idxmax()][['1_min', 'router_id', 'signal', 'user_mac']]

  routes = pd.DataFrame(data.groupby('user_mac')['router_id'].unique())
  routes = routes.reset_index()

  lists = [i.tolist() for i in routes['router_id']]

  popular_patterns = lists

  coordinates_list = transform_into_coordinates(popular_patterns, ROUTER_GEOM)
  
  return coordinates_list


def add_layer(fg, data,  color):
  routes = generate_routes(data)
  for pattern in routes:
    for point in pattern:
      folium.Circle(
            location=point,
            color=color,
            radius=150,
            fill=True,
            fill_opacity = 0.01,
            opacity=OPACITY,
        ).add_to(fg)


def create_map_day():
    map_object = folium.Map(location=(54.18133, 37.604794), zoom_start=15)

    morning_fg = folium.FeatureGroup(name="Morning", show=True).add_to(map_object)
    afternoon_fg = folium.FeatureGroup(name="Afternoon", show=False).add_to(map_object)
    evening_fg = folium.FeatureGroup(name="Evening", show=False).add_to(map_object)

    add_layer(morning_fg, morning, 'blue')
    add_layer(afternoon_fg, afternoon, 'red')
    add_layer(evening_fg, evening, 'green')

    folium.LayerControl().add_to(map_object)

    return map_object


def create_map_week():
  map_object = folium.Map(location=(54.18133, 37.604794), zoom_start=15)

  weekdays_fg = folium.FeatureGroup(name="Weekdays", show = True).add_to(map_object)
  weekends_fg = folium.FeatureGroup(name="Weekends", show = False).add_to(map_object)

  add_layer(weekdays_fg, weekdays, 'blue')
  add_layer(weekends_fg, weekends, 'green')

  folium.LayerControl().add_to(map_object)

  return map_object


def calculate_mean_time(data):
  data = data.loc[data.groupby(['user_mac', '1_min'])['signal'].idxmax()][['1_min', 'router_id', 'user_mac']]

  routes = pd.DataFrame(data.groupby('user_mac')['router_id'].unique())
  routes = routes.reset_index()

  routes = routes[routes['router_id'].apply(lambda x: len(x) >= 3)]

  first_last_time = data.groupby('user_mac')['1_min'].agg(['min', 'max']).reset_index()

  df = pd.merge(routes, first_last_time, on='user_mac', how='left')

  df['first_router'] = df['router_id'].apply(return_first)
  df['last_router'] = df['router_id'].apply(return_last)

  df['time_spent'] = df.apply(lambda row: (datetime.combine(datetime.today(), row['max']) - datetime.combine(datetime.today(), row['min'])) // timedelta(minutes=1), axis=1)

  df['first_router'] = transform_into_coordinates([[i] for i in df['first_router'].tolist()], ROUTER_GEOM)
  df['last_router'] = transform_into_coordinates([[i] for i in df['last_router'].tolist()], ROUTER_GEOM)

  return df[['first_router', 'last_router', 'time_spent']].sort_values(by = 'time_spent', ascending = False)



