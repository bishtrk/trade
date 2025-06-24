#!/usr/bin/env python3
import pandas as pd
import numpy as np
import mplfinance as mpf

def find_local_minima(series, order=2):
    is_min = pd.Series(True, index=series.index)
    for i in range(1, order+1):
        is_min &= (series < series.shift(i)) & (series < series.shift(-i))
    return is_min

def compute_trailing_stop_series(df, entry_date, order=2):
    """
    Compute a trailing stop series for longs: the most recent higher low after entry.
    """
    lows = df['Low']
    minima_mask = find_local_minima(lows, order)
    swings = lows[minima_mask & (lows.index > entry_date)]
    trailing = []
    last = None
    for date, price in swings.iteritems():
        if last is None or price > last:
            last = price
        trailing.append((date, last))
    if not trailing:
        return pd.Series(dtype=float)
    return pd.Series(
        data=[val for _, val in trailing],
        index=[dt for dt, _ in trailing]
    )

def main():
    # Load data
    df = pd.read_csv('scrip.csv', thousands=',')
    df.columns = df.columns.str.strip()
    df.rename(columns={
        'Open Price':'Open',
        'High Price':'High',
        'Low Price':'Low',
        'Close Price':'Close',
        'Total Traded Quantity':'Volume'
    }, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    ohlc = df[['Open','High','Low','Close','Volume']]

    # Compute SMAs
    ohlc['SMA20'] = ohlc['Close'].rolling(20).mean()
    ohlc['SMA50'] = ohlc['Close'].rolling(50).mean()

    # Define your entry date
    entry_date = pd.Timestamp('2025-06-20')

    # Compute trailing stop
    ts_series = compute_trailing_stop_series(ohlc, entry_date, order=2)

    # Prepare addplots
    apds = [
        mpf.make_addplot(ohlc['SMA20'], color='blue'),
        mpf.make_addplot(ohlc['SMA50'], color='orange'),
        mpf.make_addplot(ts_series, type='line', color='red', linestyle='--')
    ]

    # Plot
    mpf.plot(
        ohlc,
        type='candle',
        style='charles',
        title='TCS Candles with SMA & Trailing Stop',
        volume=True,
        addplot=apds,
        figsize=(14,8),
        ylabel='Price (₹)'
    )

if __name__ == '__main__':
    main()
