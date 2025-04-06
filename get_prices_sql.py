#Importing libraries
import pandas as pd
import sqlite3

import warnings
warnings.filterwarnings('ignore')


def get_tickers_prices_sql(tickers, db_path="moex_candles.db"):
    # Подключение к базе данных
    conn = sqlite3.connect(db_path)

    # Формирование строки запроса
    tickers_placeholder = ", ".join(["?"] * len(tickers))
    query = f"""
        SELECT tradedate, ticker, close
        FROM candles
        WHERE ticker IN ({tickers_placeholder})
        ORDER BY tradedate
    """

    # Выполняем запрос
    df = pd.read_sql(query, conn, params=tickers)
    conn.close()

    # Преобразуем данные в требуемый формат
    df_pivot = df.pivot(index="tradedate", columns="ticker", values="close")
    df_pivot.index = pd.to_datetime(df_pivot.index)  # Преобразуем TRADEDATE в формат даты
    df_pivot = df_pivot.sort_index()  # Сортируем по дате
    
    return df_pivot
