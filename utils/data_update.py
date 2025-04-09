# Import libraries
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta, date
import requests
from time import sleep

# Classify by table name
def classify_by_table_name(table_name):
    table_name = table_name.lower()
    if table_name == "stock_values":
        return "stock", "TQBR"
    elif table_name == "index_values":
        return "index", None
    elif table_name == "currency_values":
        return "currency", "CETS"
    else:
        raise ValueError(f"Неизвестное имя таблицы: {table_name}")

# Merge new and existing CSVs
def merge_and_save_csv(csv_path, df_new, subset_cols):
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path, parse_dates=["tradedate"])
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.drop_duplicates(subset=subset_cols, keep="last", inplace=True)
    else:
        df_combined = df_new
    df_combined.to_csv(csv_path, index=False)

# Fetching data from MOEX's server
def fetch_candles(ticker, board='TQBR', start_date="1995-01-01", end_date=None, instrument_type="stock"):
    if end_date is None:
        end_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    all_data = []
    start = 0

    if instrument_type == "stock":
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/{board}/securities/{ticker}/candles.json"
        params = {
            "from": start_date,
            "till": end_date,
            "interval": 24,
            "iss.meta": "off",
            "iss.json": "extended",
            "candles.columns": "begin,open,high,low,close,value,volume"
        }

        while True:
            try:
                r = requests.get(url, params={**params, "start": start}, timeout=15)
                r.raise_for_status()
                data = r.json()
                candles = data[1].get("candles", [])
                if not candles:
                    break
                all_data.extend(candles)
                start += 500
                sleep(0.2)
            except Exception as e:
                print(f"Error fetching {ticker} (stock): {e}")
                break

        if not all_data:
            return pd.DataFrame()

        df = pd.DataFrame(all_data, columns=["begin", "open", "high", "low", "close", "value", "volume"])
        df.rename(columns={"begin": "tradedate"}, inplace=True)
        df["tradedate"] = pd.to_datetime(df["tradedate"]).dt.date
        df['ticker'] = ticker

    elif instrument_type == "index":
        url = f"https://iss.moex.com/iss/history/engines/stock/markets/index/securities/{ticker}.json"
        params = {
            'from': start_date,
            'till': end_date,
            'iss.meta': 'off',
            'history.columns': 'TRADEDATE,OPEN,CLOSE,LOW,HIGH,VALUE,DURATION,YIELD,CAPITALIZATION',
            'limit': 100
        }

        while True:
            try:
                r = requests.get(url, params={**params, "start": start}, timeout=15)
                r.raise_for_status()
                data = r.json()

                if 'history' not in data or not data['history'].get('data'):
                    print(f"Ошибка: нет данных для {ticker} на {start_date} - {end_date}")
                    break

                all_data.extend(data['history']['data'])

                if len(data['history']['data']) < params['limit']:
                    break

                start += params['limit']
                sleep(0.2)
            except Exception as e:
                print(f"Error fetching {ticker} (index): {e}, URL: {r.url}")
                break

        if not all_data:
            print("Данные отсутствуют!")
            return pd.DataFrame()

        # Извлекаем столбцы из meta данных (если они указаны в ответе)
        columns = data['history'].get('columns', [])
        if not columns:
            print("Не удалось извлечь столбцы из ответа API.")
            return pd.DataFrame()

        df = pd.DataFrame(all_data, columns=columns)

        # Приводим столбцы к нижнему регистру
        df.columns = [col.lower() for col in df.columns]

        # Дополнительная проверка на пустые данные
        if df.empty:
            print(f"Нет данных для {ticker}")
            return pd.DataFrame()

        df['secid'] = ticker
        df["tradedate"] = pd.to_datetime(df["tradedate"]).dt.date

    elif instrument_type == "currency":
        url = f"https://iss.moex.com/iss/history/engines/currency/markets/selt/boards/{board}/securities/{ticker}.json"
        params = {
            "from": start_date,
            "till": end_date,
            "iss.meta": "off",
            "history.columns": "TRADEDATE,SECID,BOARDID,OPEN,CLOSE,LOW,HIGH,NUMTRADES,VOLRUR,WAPRICE",
            "limit": 100,
            "start": start
        }

        while True:
            try:
                r = requests.get(url, params=params, timeout=15)
                r.raise_for_status()
                data = r.json()
                rows = data.get("history", {}).get("data", [])
                if not rows:
                    break
                all_data.extend(rows)
                start += 100
                params["start"] = start
                sleep(0.2)
            except Exception as e:
                print(f"Error fetching {ticker} (gold): {e}")
                break

        if not all_data:
            print("Данные отсутствуют!")
            return pd.DataFrame()

        # Извлекаем столбцы из meta данных (если они указаны в ответе)
        columns = data['history'].get('columns', [])
        if not columns:
            print("Не удалось извлечь столбцы из ответа API.")
            return pd.DataFrame()

        df = pd.DataFrame(all_data, columns=columns)

        # Приводим столбцы к нижнему регистру
        df.columns = [col.lower() for col in df.columns]

        # Дополнительная проверка на пустые данные
        if df.empty:
            print(f"Нет данных для {ticker}")
            return pd.DataFrame()

        df['secid'] = ticker
        df["tradedate"] = pd.to_datetime(df["tradedate"]).dt.date

    else:
        raise ValueError(f"Unknown instrument_type: {instrument_type}")

    return df

# SQL base + CSV update
def update_data(ticker, db_path="moex_data.db", table_name="stock_values", csv_dir="csv_data/stock"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # определяем тип инструмента по таблице
    instrument_type, board = classify_by_table_name(table_name)

    if instrument_type == 'stock':
        cursor.execute(f"""
            SELECT MAX(tradedate) FROM {table_name}
            WHERE ticker = ?;
        """, (ticker,))
        result = cursor.fetchone()
        last_date = result[0]
    elif instrument_type == 'index':
        cursor.execute(f"""
            SELECT MAX(tradedate) FROM {table_name}
            WHERE secid = ?;
        """, (ticker,))
        result = cursor.fetchone()
        last_date = result[0]
    elif instrument_type == 'currency':
        cursor.execute(f"""
            SELECT MAX(tradedate) FROM {table_name}
            WHERE secid = ?;
        """, (ticker,))
        result = cursor.fetchone()
        last_date = result[0]


    if last_date:
        if isinstance(last_date, str):
            try:
                start_date = datetime.strptime(last_date, "%Y-%m-%d").date() + timedelta(days=1)
            except ValueError:
                print(f"Невозможно распарсить дату: {last_date}")
                conn.close()
                return
        elif isinstance(last_date, datetime):
            start_date = last_date.date() + timedelta(days=1)
        elif isinstance(last_date, date):
            start_date = last_date + timedelta(days=1)
        else:
            print(f"Неподдерживаемый тип даты: {type(last_date)}")
            conn.close()
            return
    else:
        start_date = datetime(1995, 1, 1).date()


    print(f"Загружаем данные для {ticker} с {start_date}")
    df_new = fetch_candles(ticker, board=board, start_date=start_date.isoformat(), instrument_type=instrument_type)

    if df_new.empty:
        print(f"Нет новых данных для {ticker}")
        conn.close()
        return

    df_new.to_sql(table_name, conn, if_exists="append", index=False)
    print(f"{len(df_new)} строк добавлено в таблицу {table_name}")

    csv_path = os.path.join(csv_dir, f"{ticker}.csv")
    merge_and_save_csv(csv_path, df_new, subset_cols=["ticker", "tradedate"])
    print(f"CSV файл обновлён: {csv_path}")

    conn.close()

# Getting all tickers from data base
def get_all_tickers(db_path="moex_data.db", table_name="stock_values"):
    # определяем тип инструмента по таблице
    instrument_type, board = classify_by_table_name(table_name)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if instrument_type == "stock":
        cursor.execute(f"SELECT DISTINCT ticker FROM {table_name}")
        tickers = [row[0] for row in cursor.fetchall()]
    elif instrument_type == "index":
        cursor.execute(f"SELECT DISTINCT secid FROM {table_name}")
        tickers = [row[0] for row in cursor.fetchall()]
    elif instrument_type == "currency":
        cursor.execute(f"SELECT DISTINCT secid FROM {table_name}")
        tickers = [row[0] for row in cursor.fetchall()]

    conn.close()
    return tickers

# Main function
def update_all_tickers(db_path="moex_data.db", table_name="stock_values", csv_dir="csv_data/stock"):
    tickers = get_all_tickers(db_path=db_path, table_name=table_name)
    for ticker in tickers:
        print(f"\n=== Обновление данных для {ticker} ===")
        update_data(ticker, db_path=db_path, table_name=table_name, csv_dir=csv_dir)


update_all_tickers(db_path="moex_data.db", table_name="stock_values", csv_dir="csv_data/stock")
update_all_tickers(db_path='moex_data.db', table_name='index_values', csv_dir="csv_data/indexes")
update_all_tickers(db_path='moex_data.db', table_name='currency_values', csv_dir="csv_data/currency")