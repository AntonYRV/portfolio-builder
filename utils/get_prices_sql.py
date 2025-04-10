#Importing libraries
import pandas as pd
import sqlite3

import warnings
warnings.filterwarnings('ignore')


def get_stock_prices_sql(tickers, start_date=None, end_date=None, db_path="moex_data.db"):
    # Подключение к базе данных
    conn = sqlite3.connect(db_path)
    
    # Формируем SQL-запрос с фильтрацией по дате
    tickers_placeholder = ", ".join(["?"] * len(tickers))
    query = f"""
        SELECT tradedate, ticker, close
        FROM stock_values
        WHERE ticker IN ({tickers_placeholder})
    """
    if start_date:
        query += " AND tradedate >= ?"
    if end_date:
        query += " AND tradedate <= ?"
    query += " ORDER BY tradedate"

    # Параметры для запроса
    params = tickers
    if start_date:
        params.append(start_date)
    if end_date:
        params.append(end_date)
    
    # Выполнение запроса
    df = pd.read_sql(query, conn, params=params)
    conn.close()

    # Преобразуем данные в нужный формат
    df_pivot = df.pivot(index="tradedate", columns="ticker", values="close")
    df_pivot.index = pd.to_datetime(df_pivot.index)
    df_pivot = df_pivot.sort_index()

    return df_pivot



def get_index_values_sql(tickers, start_date=None, end_date=None, db_path="moex_data.db"):
    # Подключение к базе данных
    conn = sqlite3.connect(db_path)
    
    # Формируем SQL-запрос с фильтрацией по дате
    tickers_placeholder = ", ".join(["?"] * len(tickers))
    query = f"""
        SELECT tradedate, secid, close
        FROM index_values
        WHERE secid IN ({tickers_placeholder})
    """
    if start_date:
        query += " AND tradedate >= ?"
    if end_date:
        query += " AND tradedate <= ?"
    query += " ORDER BY tradedate"

    # Параметры для запроса
    params = tickers
    if start_date:
        params.append(start_date)
    if end_date:
        params.append(end_date)
    
    # Выполнение запроса
    df = pd.read_sql(query, conn, params=params)
    conn.close()

    # Преобразуем данные в нужный формат
    df_pivot = df.pivot(index="tradedate", columns="secid", values="close")
    df_pivot.index = pd.to_datetime(df_pivot.index)
    df_pivot = df_pivot.sort_index()

    return df_pivot


def get_currency_prices_sql(tickers, start_date=None, end_date=None, db_path="moex_data.db"):
    # Подключение к базе данных
    conn = sqlite3.connect(db_path)
    
    # Формируем SQL-запрос с фильтрацией по дате
    tickers_placeholder = ", ".join(["?"] * len(tickers))
    query = f"""
        SELECT tradedate, secid, close
        FROM currency_values
        WHERE secid IN ({tickers_placeholder})
    """
    if start_date:
        query += " AND tradedate >= ?"
    if end_date:
        query += " AND tradedate <= ?"
    query += " ORDER BY tradedate"

    # Параметры для запроса
    params = tickers
    if start_date:
        params.append(start_date)
    if end_date:
        params.append(end_date)
    
    # Выполнение запроса
    df = pd.read_sql(query, conn, params=params)
    conn.close()

    # Преобразуем данные в нужный формат
    df_pivot = df.pivot(index="tradedate", columns="secid", values="close")
    df_pivot.index = pd.to_datetime(df_pivot.index)
    df_pivot = df_pivot.sort_index()

    return df_pivot

def get_assets_prices_sql(tickers, start_date=None, end_date=None, db_path="moex_data.db"):
    # Подключение к базе данных
    conn = sqlite3.connect(db_path)
    
    # Формируем плейсхолдеры для тикеров
    tickers_placeholder = ", ".join(["?"] * len(tickers))
    
    # Формируем SQL-запрос с фильтрацией по дате
    query = f"""
        SELECT tradedate, secid, close
        FROM index_values
        WHERE secid IN ({tickers_placeholder})
    """
    
    # Добавляем фильтрацию по датам для первого подзапроса
    if start_date:
        query += " AND tradedate >= ?"
    if end_date:
        query += " AND tradedate <= ?"
    
    # Добавляем UNION ALL и второй подзапрос для валют
    query += " UNION ALL "
    
    query += f"""
        SELECT tradedate, secid, close
        FROM currency_values
        WHERE secid IN ({tickers_placeholder})
    """
    
    # Добавляем фильтрацию по датам для второго подзапроса
    if start_date:
        query += " AND tradedate >= ?"
    if end_date:
        query += " AND tradedate <= ?"
    
    # Завершаем запрос
    query += " ORDER BY tradedate"
    
    # Параметры для запроса: тикеры для обеих таблиц и даты (если есть)
    params = tickers.copy()  # Копируем тикеры для обеих таблиц
    if start_date:
        params.append(start_date)  # Добавляем start_date
    if end_date:
        params.append(end_date)  # Добавляем end_date
    
    params += tickers  # Дублируем тикеры для второго подзапроса
    if start_date:
        params.append(start_date)  # Добавляем start_date для валют
    if end_date:
        params.append(end_date)  # Добавляем end_date для валют

    # Выполнение запроса
    df = pd.read_sql(query, conn, params=params)
    conn.close()

    # Преобразуем данные в нужный формат
    df_pivot = df.pivot(index="tradedate", columns="secid", values="close")
    df_pivot.index = pd.to_datetime(df_pivot.index)
    df_pivot = df_pivot.sort_index()

    return df_pivot
