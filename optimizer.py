import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.optimize import minimize
from data_loader import index_history

import warnings
warnings.filterwarnings('ignore')

def expected_return(weights, log_returns):
    return np.sum(log_returns.mean() * weights) * 252

def standard_deviation(weights, cov_matrix):
    variance = weights.T @ cov_matrix @ weights
    return np.sqrt(variance)

def sharpe_ratio(weights, log_returns, cov_matrix, rf):
    return (expected_return(weights, log_returns) - rf) / standard_deviation(weights, cov_matrix)

def neg_sharpe_ratio(weights, log_returns, cov_matrix, rf):
    return -sharpe_ratio(weights, log_returns, cov_matrix, rf)

def optimize_portfolio(tickers, start_date, end_date, rf=0):
    data = index_history(tickers, start_date=start_date, end_date=end_date)
    data = data.set_index('TRADEDATE')

    log_returns = np.log(data / data.shift(1)).dropna()
    cov_matrix = log_returns.cov() * 252

    constraints = {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}
    bounds = [(0, 1) for _ in range(len(tickers))]
    initial_weights = np.array([1 / len(tickers)] * len(tickers))

    optimized_results = minimize(
        neg_sharpe_ratio, 
        initial_weights, 
        args=(log_returns, cov_matrix, rf), 
        method='SLSQP', 
        constraints=constraints, 
        bounds=bounds
    )

    optimal_weights = optimized_results.x
    optimal_portfolio_return = expected_return(optimal_weights, log_returns)
    optimal_portfolio_volatility = standard_deviation(optimal_weights, cov_matrix)
    optimal_sharpe_ratio = sharpe_ratio(optimal_weights, log_returns, cov_matrix, rf)

    return {
        "weights": {ticker: round(weight, 4) for ticker, weight in zip(tickers, optimal_weights)},
        "expected_return": round(optimal_portfolio_return, 4),
        "volatility": round(optimal_portfolio_volatility, 4),
        "sharpe_ratio": round(optimal_sharpe_ratio, 4)
    }
