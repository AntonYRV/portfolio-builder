#Importing libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from skfolio import Population, RiskMeasure
from skfolio.optimization import InverseVolatility, MeanRisk, ObjectiveFunction
from skfolio.preprocessing import prices_to_returns
from data_loader import index_history
from data_loader import ticker_prices

import warnings
warnings.filterwarnings('ignore')


#Optimizing function
def optimizer(tickers, rf, start_date="2000-01-01", end_date=None):
    
    rf_daily = rf / 252

    #Loading data
    data = ticker_prices(tickers, start_date=start_date, end_date=end_date)
    data = data.set_index('TRADEDATE')

    # Convert prices to returns
    returns = prices_to_returns(data, log_returns=True, fill_nan=False)

    model = MeanRisk(
        risk_measure=RiskMeasure.STANDARD_DEVIATION,
        objective_function=ObjectiveFunction.MAXIMIZE_RATIO,
        portfolio_params=dict(name="Max Sharpe"),
        risk_free_rate=rf_daily,
        )

    model.fit(returns)


    weights = model.weights_
    optimal_portfolio_return_daily = returns.dot(weights)
    optimal_portfolio_return = optimal_portfolio_return_daily.mean() * 252
    optimal_portfolio_volatility_daily = optimal_portfolio_return_daily.std()
    optimal_portfolio_volatility = optimal_portfolio_volatility_daily * np.sqrt(252)
    optimal_sharpe_ratio = (optimal_portfolio_return - rf) / optimal_portfolio_volatility

    return {
        "weights": {ticker: round(weight, 4) for ticker, weight in zip(tickers, weights)},
        "expected_return": round(optimal_portfolio_return, 4),
        "volatility": round(optimal_portfolio_volatility, 4),
        "sharpe_ratio": round(optimal_sharpe_ratio, 4)
        }

