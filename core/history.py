import sqlite3
import pandas as pd
import numpy as np

#The function makes the appropriate queries to the correct tables depending on the asset type
def get_asset_data(tickers, start_date, end_date, asset_type):
    conn = sqlite3.connect("moex_data.db")
    placeholders = ', '.join(['?'] * len(tickers)) #Create a list of "?" for the query
    
    if asset_type == 'stock':
        query = f"""
            SELECT ticker as asset_id, tradedate, close
            FROM stock_values
            WHERE ticker IN ({placeholders}) AND tradedate BETWEEN ? AND ?
            ORDER BY ticker, tradedate
        """
    elif asset_type == 'index':
        query = f"""
            SELECT secid as asset_id, tradedate, close
            FROM index_values
            WHERE secid IN ({placeholders}) AND tradedate BETWEEN ? AND ?
            ORDER BY secid, tradedate
        """
    elif asset_type == 'currency':
        query = f"""
            SELECT secid as asset_id, tradedate, close
            FROM currency_values
            WHERE secid IN ({placeholders}) AND tradedate BETWEEN ? AND ?
            ORDER BY secid, tradedate
        """
    
    params = tickers + [start_date, end_date]
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

#Creating an investment portfolio history
def get_portfolio_history(weights_dict, start_date, end_date, initial_portfolio_value=1000000, mode='tickers'):
    
    # Create variables for different types of assets
    stock_tickers = []
    index_tickers = []
    currency_tickers = []

    # Formation of a list of tickers from a dictionary, depending on the type of optimization
    for ticker in weights_dict:
        if mode == 'tickers':
            stock_tickers.append(ticker)
        elif mode == 'assets':
            if ticker == 'GLDRUB_TOM':
                currency_tickers.append(ticker)
            else:
                index_tickers.append(ticker)
    
    # Retrieve data in one request for each asset type
    dfs = []
    date_ranges = {}
    
    if stock_tickers:
        stock_df = get_asset_data(stock_tickers, start_date, end_date, 'stock')
        stock_df["tradedate"] = pd.to_datetime(stock_df["tradedate"])
        if not stock_df.empty:
            dfs.append(stock_df)
    
    if index_tickers:
        index_df = get_asset_data(index_tickers, start_date, end_date, 'index')
        index_df["tradedate"] = pd.to_datetime(index_df["tradedate"])
        if not index_df.empty:
            dfs.append(index_df)
    
    if currency_tickers:
        currency_df = get_asset_data(currency_tickers, start_date, end_date, 'currency')
        currency_df["tradedate"] = pd.to_datetime(currency_df["tradedate"])
        if not currency_df.empty:
            dfs.append(currency_df)
    
    if not dfs:
        return pd.DataFrame(), "No data for selected securities."
    
    # Combining data
    all_data = pd.concat(dfs)

    # Create a pivot table with asset prices
    price_pivot = all_data.pivot_table(index='tradedate', columns='asset_id', values='close')

    # Calculating returns
    price_pivot = price_pivot.replace(0, method='ffill')
    price_pivot = price_pivot[price_pivot.ne(0).any(axis=1)]
    price_pivot = price_pivot.dropna(how='any')

    returns = np.log(price_pivot / price_pivot.shift(1)).dropna()

    # Applying weights
    weighted_returns = pd.DataFrame()
    for col in returns.columns:
        if col in weights_dict:
            weighted_returns[col] = returns[col] * weights_dict[col]
    
    # Sum of total portfolio return by dates
    portfolio_return = weighted_returns.sum(axis=1)
    
    # Calculating the value of the portfolio
    portfolio_value = initial_portfolio_value * np.exp(portfolio_return.cumsum())
    result_df = pd.DataFrame({'portfolio_value': portfolio_value})
    
    # Define a date range for a message
    for ticker in weights_dict:
        ticker_data = price_pivot[ticker].dropna()
        if not ticker_data.empty:
            date_ranges[ticker] = (ticker_data.index.min().date(), ticker_data.index.max().date())
    
    if date_ranges:
        min_date = max(start for start, _ in date_ranges.values())
        max_date = min(end for _, end in date_ranges.values())
        message = (
            f"История портфеля отображается с {min_date} по {max_date}, "
            f"так как некоторые бумаги имеют ограниченные данные."
        )
    else:
        message = "Нет данных по выбранным бумагам."
    
    # Returns df and message
    return result_df.reset_index(), message
