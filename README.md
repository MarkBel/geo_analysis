# Geo optimization

The current application functionality includes:
* Routes info
* EDA
* Optimal route calculator
* Alternative data EDA


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



