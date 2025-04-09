#Importing libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from utils.data_loader import index_history
from utils.data_loader import ticker_prices #No need?
from utils.get_prices_sql import get_stock_prices_sql, get_index_values_sql, get_currency_prices_sql
from pypfopt import expected_returns, risk_models, EfficientFrontier, objective_functions

import warnings
warnings.filterwarnings('ignore')



def optimizer_for_tickers(tickers, rf=0.0, start_date="2000-01-01", end_date=None, 
              objective="max_sharpe", risk_aversion=1.0, 
              target_volatility=None, target_return=None, 
              short_positions=False, l2_reg=False, gamma=1):  # Новый параметр для включения/выключения L2 регуляризации

    df = get_stock_prices_sql(tickers, start_date=start_date, end_date=end_date)

    
    # Ожидаемые доходности и ковариационная матрица
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)

    # Создание объекта EfficientFrontier для оптимизации с возможностью шортов
    ef = EfficientFrontier(mu, S, weight_bounds=(-2, 1) if short_positions else (0, 1), solver="ECOS")

    # Добавляем регуляризацию L2, если включена
    if l2_reg:
        ef.add_objective(objective_functions.L2_reg, gamma=gamma)  # Регуляризация L2 с параметром gamma

     # Проверка на допустимость целевой доходности для efficient_return
    if objective == "efficient_return":
        min_return = mu.min()  # Минимальная возможная доходность
        max_return = mu.max()  # Максимальная возможная доходность
        if target_return < min_return or target_return > max_return:
            raise ValueError(f"Целевая доходность выходит за пределы допустимого диапазона: "
                             f"Минимальная возможная доходность: {min_return:.8f}, "
                             f"Максимальная возможная доходность: {max_return:.8f}.")

    # Выбор метода оптимизации
    if objective == "max_sharpe":
        # Оптимизация для максимизации Sharpe Ratio
        ef.max_sharpe(risk_free_rate=rf)
    elif objective == "max_quadratic_utility":
        # Оптимизация для максимизации квадратичной полезности
        ef.max_quadratic_utility(risk_aversion=risk_aversion)
    elif objective == "efficient_risk":
        # Оптимизация для достижения определенного уровня риска
        if target_volatility is None:
            raise ValueError("Для 'efficient_risk' необходимо указать target_volatility.")
        ef.efficient_risk(target_volatility=target_volatility)
    elif objective == "efficient_return":
        # Оптимизация для достижения определенного уровня доходности
        if target_return is None:
            raise ValueError("Для 'efficient_return' необходимо указать target_return.")
        ef.efficient_return(target_return=target_return)
    elif objective == "min_volatility":
        ef.min_volatility()
    else:
        raise ValueError(f"Неизвестный метод оптимизации: {objective}")

    # Получение оптимальных весов активов
    weights = ef.clean_weights()

    # Оценка производительности портфеля
    performance = ef.portfolio_performance(verbose=True)

    return {
        "weights": {ticker: round(weight, 4) for ticker, weight in weights.items()},
        "performance": {"return": performance[0], 
                        "volatility": performance[1], 
                        "sharpe_ratio": performance[2]}
    }


def optimizer_for_assets(secids, rf=0.0, start_date="2000-01-01", end_date=None, 
              objective="max_sharpe", risk_aversion=1.0, 
              target_volatility=None, target_return=None, 
              short_positions=False, l2_reg=False, gamma=1):  # Новый параметр для включения/выключения L2 регуляризации

    df = get_index_values_sql(secids, start_date=start_date, end_date=end_date)
    
    # Ожидаемые доходности и ковариационная матрица
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)

    # Создание объекта EfficientFrontier для оптимизации с возможностью шортов
    ef = EfficientFrontier(mu, S, weight_bounds=(-2, 1) if short_positions else (0, 1), solver="ECOS")

    # Добавляем регуляризацию L2, если включена
    if l2_reg:
        ef.add_objective(objective_functions.L2_reg, gamma=gamma)  # Регуляризация L2 с параметром gamma

     # Проверка на допустимость целевой доходности для efficient_return
    if objective == "efficient_return":
        min_return = mu.min()  # Минимальная возможная доходность
        max_return = mu.max()  # Максимальная возможная доходность
        if target_return < min_return or target_return > max_return:
            raise ValueError(f"Целевая доходность выходит за пределы допустимого диапазона: "
                             f"Минимальная возможная доходность: {min_return:.8f}, "
                             f"Максимальная возможная доходность: {max_return:.8f}.")

    # Выбор метода оптимизации
    if objective == "max_sharpe":
        # Оптимизация для максимизации Sharpe Ratio
        ef.max_sharpe(risk_free_rate=rf)
    elif objective == "max_quadratic_utility":
        # Оптимизация для максимизации квадратичной полезности
        ef.max_quadratic_utility(risk_aversion=risk_aversion)
    elif objective == "efficient_risk":
        # Оптимизация для достижения определенного уровня риска
        if target_volatility is None:
            raise ValueError("Для 'efficient_risk' необходимо указать target_volatility.")
        ef.efficient_risk(target_volatility=target_volatility)
    elif objective == "efficient_return":
        # Оптимизация для достижения определенного уровня доходности
        if target_return is None:
            raise ValueError("Для 'efficient_return' необходимо указать target_return.")
        ef.efficient_return(target_return=target_return)
    elif objective == "min_volatility":
        ef.min_volatility()
    else:
        raise ValueError(f"Неизвестный метод оптимизации: {objective}")

    # Получение оптимальных весов активов
    weights = ef.clean_weights()

    # Оценка производительности портфеля
    performance = ef.portfolio_performance(verbose=True)

    return {
        "weights_dict": {ticker: round(weight, 4) for ticker, weight in weights.items()},
        "performance": {"return": performance[0], 
                        "volatility": performance[1], 
                        "sharpe_ratio": performance[2]}
    }
