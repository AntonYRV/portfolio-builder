# Import libraries
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

#Fetching data from MOEX's server
def fetch_candles(ticker, board='TQBR', start_date="2000-01-01"):
    import requests
    from time import sleep

    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/{board}/securities/{ticker}/candles.json"
    params = {
        "from": start_date,
        "interval": 24,
        "iss.meta": "off",
        "iss.json": "extended",
        "candles.columns": "begin,open,high,low,close,value,volume"
    }

    all_data = []
    start = 0

    while True:
        try:
            r = requests.get(url, params={**params, "start": start}, timeout=15)
            r.raise_for_status()
            data = r.json()

            if len(data) < 2 or "candles" not in data[1]:
                break

            candles = data[1]["candles"]
            if not candles:
                break

            all_data.extend(candles)

            start += 500
            sleep(0.2)

        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            break

    if not all_data:
        return pd.DataFrame()

    df = pd.DataFrame(all_data, columns=["begin", "open", "high", "low", "close", "value", "volume"])
    df.rename(columns={"begin": "tradedate"}, inplace=True)
    df["tradedate"] = pd.to_datetime(df["tradedate"]).dt.date
    df.insert(0, "ticker", ticker)
    df["boardid"] = board

    return df

#SQL base + csv update
def update_data(ticker, db_path="moex_candles.db", table_name="candles", csv_dir="csv_data"):
    # Подключение к базе
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Проверка последней даты в БД
    cursor.execute(f"""
        SELECT MAX(tradedate) FROM {table_name}
        WHERE ticker = ?;
    """, (ticker,))
    result = cursor.fetchone()
    last_date = result[0]

    if last_date:
        start_date = datetime.strptime(last_date, "%Y-%m-%d").date() + timedelta(days=1)
    else:
        start_date = datetime(2000, 1, 1).date()

    print(f"Загружаем данные для {ticker} с {start_date}")

    df_new = fetch_candles(ticker, start_date=start_date.isoformat())

    if df_new.empty:
        print(f"Нет новых данных для {ticker}")
        conn.close()
        return

    # Добавляем в БД
    df_new.to_sql(table_name, conn, if_exists="append", index=False)
    print(f"{len(df_new)} строк добавлено в таблицу {table_name}")

    # Добавляем в CSV
    csv_path = os.path.join(csv_dir, f"{ticker}.csv")
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path, parse_dates=["tradedate"])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.drop_duplicates(subset=["ticker", "tradedate"], keep="last", inplace=True)
    else:
        df_combined = df_new

    df_combined.to_csv(csv_path, index=False)
    print(f"CSV файл обновлён: {csv_path}")

    conn.close()

#Getting all tickers from data base
def get_all_tickers(db_path="moex_candles.db", table_name="candles"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT DISTINCT ticker FROM {table_name}")
    tickers = [row[0] for row in cursor.fetchall()]

    conn.close()
    return tickers

#Main function
def update_all_tickers(db_path="moex_candles.db", table_name="candles", csv_dir="csv_data"):
    tickers = get_all_tickers(db_path, table_name)
    print(f"Найдено {len(tickers)} тикеров в базе.")

    for ticker in tickers:
        print(f"\n=== Обновление данных для {ticker} ===")
        update_data(ticker, db_path=db_path, table_name=table_name, csv_dir=csv_dir)


update_all_tickers()