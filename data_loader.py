import pandas as pd
import numpy as np
import yfinance as yf
import requests
import apimoex
from datetime import datetime, timedelta
from scipy.optimize import minimize

import warnings
warnings.filterwarnings('ignore')

def get_ticker_history(ticker, start_date="2000-01-01", end_date=None):
    """
    Получает дневную историю цен для указанного тикера.
    
    Параметры:
    - ticker: str, тикер бумаги (например, SBER, GAZP)
    - start_date: str, дата начала в формате YYYY-MM-DD
    - end_date: str, дата окончания (по умолчанию — сегодня)
    
    Возвращает:
    - DataFrame с колонками: TRADEDATE, CLOSE, VOLUME
    """
    if end_date is None:
        end_date = pd.Timestamp.today().strftime('%Y-%m-%d')

    with requests.Session() as session:
        try:
            data = apimoex.get_market_candles(session, ticker, interval=24, start=start_date, end=end_date)
        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
            return None
    
    df = pd.DataFrame(data)
    
    if df.empty:
        return None
    
    df["TRADEDATE"] = pd.to_datetime(df["begin"])
    df = df[["TRADEDATE", "close"]]
    df.rename(columns={"close": ticker}, inplace=True)
    return df

#Получить данные из списка тикеров
def ticker_prices(tickers, start_date="2000-01-01", end_date=None):
    
    """
    Получает дневную историю цен для указанного тикера.
    
    Параметры:
    - ticker: str, тикер бумаги (например, SBER, GAZP)
    - start_date: str, дата начала в формате YYYY-MM-DD
    - end_date: str, дата окончания (по умолчанию — сегодня)
    
    Возвращает:
    - DataFrame с колонками: TRADEDATE, CLOSE, VOLUME
    """
    if end_date is None:
        end_date = pd.Timestamp.today()
    
    # Преобразуем в строку после вычислений
    end_date = end_date.strftime('%Y-%m-%d')

    # Если передан один индекс, превращаем его в список
    if isinstance(tickers, str):
        tickers = [tickers]
    
    # Список для хранения данных по индексам
    dfs = []
    
    for ticker in tickers:
        df = get_ticker_history(ticker, start_date, end_date)
        if df is not None:  # добавляем проверку на пустой DataFrame
            dfs.append(df)

    # Объединяем все DataFrame по TRADEDATE
    df_combined = dfs[0]
    for df in dfs[1:]:
        df_combined = pd.merge(df_combined, df, on="TRADEDATE", how="outer")
    
    # Сортируем по дате
    df_combined = df_combined.sort_values("TRADEDATE")
    
    return df_combined

def get_index_data(index='IMOEX', start_date="2000-01-01", end_date=None):
    '''
    IMOEX - Мосбиржа
    RTSI - РТС
    MCFTR - Мосбиржа, полная доходность
    MESMTR - Средняя и малая капитализаци, полная доходность
    MEBCTR - Голубые фишки, полная доходность 
    MOEXBMI - Широкий рынок, 100 компаний
    MCXSM - Средняя и малая капитализаци

    MOEXOG - Нефть и газ
    MOEXEU - Электро
    MOEXTL - Телекоммуникации
    MOEXMM - Металлы и добыча
    MOEXFN - Финансы
    MOEXCN - Потреб сектор
    MOEXCH - Химия и нефтехимия
    MOEXIT - ИТ
    MOEXRE - Недвижимость
    MOEXTN - Транспорт

    RGBITR - Гос облигации
    RUCBITR - Корп облигации
    RUCBICP - Ценовой индекс корп облигаций
    '''
        
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
   
    with requests.Session() as session:
        # Получаем исторические данные для индекса IMOEX
        # Здесь market="index", engine по умолчанию "stock" подходит для индексов
        data = apimoex.get_market_history(
            session,
            security=index,
            start=start_date,
            end=end_date,
            market="index",  # именно для индексов
            engine="stock"
        )
        
    # Преобразуем полученные данные в DataFrame
    df = pd.DataFrame(data)
    df = df[["TRADEDATE", "CLOSE"]]  # Берем только нужные столбцы
    df.rename(columns={"CLOSE": index}, inplace=True)  # Переименовываем столбец
    return df

#Получение исторических данных по 1 или нескольким индексам
def index_history(index='IMOEX', start_date="2000-01-01", end_date=None):
    '''
    Функция для получения исторических данных по одному или нескольким индексам.
    Если передан список индексов, то данные для них будут объединены по дате.
    
    Пример:
    index_history(index=['IMOEX', 'RTSI'], start_date="2000-01-01", end_date="2025-01-01")
    '''
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    
    # Если передан один индекс, превращаем его в список
    if isinstance(index, str):
        index = [index]
    
    # Список для хранения данных по индексам
    dfs = []
    
    for ind in index:
        # Получаем данные для каждого индекса
        df = get_index_data(ind, start_date, end_date)
        dfs.append(df)
    
    # Объединяем все DataFrame по TRADEDATE
    df_combined = dfs[0]
    for df in dfs[1:]:
        df_combined = pd.merge(df_combined, df, on="TRADEDATE", how="outer")
    
    # Сортируем по дате
    df_combined = df_combined.sort_values("TRADEDATE")
    
    return df_combined

