#Importing libraries
import pandas as pd
import sqlite3

import warnings
warnings.filterwarnings('ignore')


def get_tickers_prices_sql(tickers, start_date=None, end_date=None, db_path="moex_candles.db"):
    # Подключение к базе данных
    conn = sqlite3.connect(db_path)
    
    # Формируем SQL-запрос с фильтрацией по дате
    tickers_placeholder = ", ".join(["?"] * len(tickers))
    query = f"""
        SELECT tradedate, ticker, close
        FROM candles
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

