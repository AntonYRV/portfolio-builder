import sqlite3
import pandas as pd
import numpy as np

def get_portfolio_history(weights_dict, start_date, end_date, initial_portfolio_value=1000000):
    conn = sqlite3.connect("moex_candles.db")
    dfs = []
    date_ranges = {}

    # Стартовая стоимость портфеля
    portfolio_value = initial_portfolio_value

    for ticker, weight in weights_dict.items():
        query = """
            SELECT tradedate, close
            FROM candles
            WHERE ticker = ? AND tradedate BETWEEN ? AND ?
            ORDER BY tradedate
        """
        df = pd.read_sql_query(query, conn, params=(ticker, start_date, end_date))
        df["tradedate"] = pd.to_datetime(df["tradedate"])
        df.set_index("tradedate", inplace=True)

        if df.empty:
            continue

        # Рассчитываем логарифмические доходности
        df["log_return"] = np.log(df["close"] / df["close"].shift(1))

        # Умножаем логарифмические доходности на вес
        df["weighted_log_return"] = df["log_return"] * weight

        # Добавляем столбец с доходностью для портфеля
        dfs.append(df[["weighted_log_return"]])

        date_ranges[ticker] = (df.index.min().date(), df.index.max().date())

    conn.close()

    # Объединяем все DataFrame
    combined = pd.concat(dfs, axis=1)
    combined.dropna(inplace=True)

    # Рассчитываем стоимость портфеля на основе логарифмических доходностей
    combined["portfolio_value"] = initial_portfolio_value * np.exp(combined.sum(axis=1).cumsum())

    if date_ranges:
        min_date = max(start for start, _ in date_ranges.values())
        max_date = min(end for _, end in date_ranges.values())
        message = (
            f"История портфеля отображается с {min_date} по {max_date}, "
            f"так как некоторые бумаги имеют ограниченные данные."
        )
    else:
        message = "Нет данных по выбранным бумагам."

    return combined[["portfolio_value"]].reset_index(), message
