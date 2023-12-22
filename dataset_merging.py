# Можно скачать папку с яндекса
import os
folder_path = '/content/sample_data/wifi_logs_2023_01'

wifi_logs = pd.DataFrame(columns = ['guid', 'tm', 'router_mac', 'user_mac', 'signal', 'router_did'])
for filename in os.listdir(folder_path):
  file_path = os.path.join(folder_path, filename)
  wifi_log = pd.read_csv(file_path, sep = ";")
  wifi_logs = pd.concat([wifi_logs, wifi_log], axis = 0)
