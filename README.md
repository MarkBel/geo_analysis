# Geo optimization

Тетрадка с экспериментом:https://colab.research.google.com/drive/1xBZ7wEz6P4yhsSHjhWKzyOz9x2LsQG5W?usp=sharing

Для запуска приложения, необходимо установить зависимости и запустить через Streamlit фреймворк:
```bash
 pip install -r requirements.txt
```

```bash
 streamlit run app.py
```


## Current libraries versions list

Use [pip]() to install.

```bash
 pip install -r requirements.txt
```

- streamlit


## Local development
Port variable is defined in the .env file

```bash
streamlit run --server.port $PORT app.py
```


## Code quality before commit


```bash
pylint path_to_file
```

```bash
black path_to_file
```

```bash
black .
```



