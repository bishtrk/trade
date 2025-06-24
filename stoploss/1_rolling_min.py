#!/usr/bin/env python3
import pandas as pd
import numpy as np

def compute_atr(df, period=14):
    """Compute the Average True Range (ATR)."""
    high_low = df['High'] - df['Low']
    high_prev_close = (df['High'] - df['Close'].shift(1)).abs()
    low_prev_close  = (df['Low']  - df['Close'].shift(1)).abs()
    true_range = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()

def find_breakouts(df, lookback=20):
    """
    Identify breakout days: Close > rolling max High over the past `lookback` days.
    Returns a boolean Series.
    """
    rolling_max = df['High'].shift(1).rolling(window=lookback).max()
    return df['Close'] > rolling_max

def compute_support(df, window=10):
    """
    Nearest support = rolling min Low over the past `window` days (excluding today).
    """
    return df['Low'].shift(1).rolling(window=window).min()

def compute_stop_levels(df,
                        breakout_lookback=20,
                        support_window=10,
                        buffer_pct=0.005,
                        atr_period=14):
    """
    For each breakout day, compute:
      - breakout_low   = Low of the breakout day
      - support_zone   = prior swing-low (nearest support)
      - buffer         = max(buffer_pct * Close, ATR)
      - stop_price     = support_zone - buffer
    """
    df = df.copy()
    # 1. ATR
    df['ATR'] = compute_atr(df, period=atr_period)

    # 2. Breakout signals
    df['Breakout'] = find_breakouts(df, lookback=breakout_lookback)

    # 3. Support zones
    df['Support'] = compute_support(df, window=support_window)

    # 4. Buffers (volatility + fixed %)
    df['Buffer'] = df[['ATR', 'Close']].apply(
        lambda x: max(x['ATR'], buffer_pct * x['Close']), axis=1
    )

    # 5. Stop price
    df['StopPrice'] = df['Support'] - df['Buffer']

    # 6. Only keep breakout days
    return df.loc[df['Breakout'], ['Close','Low','Support','ATR','Buffer','StopPrice']]

def main():
    # --- Load & prepare data ---
    df = pd.read_csv('scrip.csv', thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'Open Price': 'Open',
        'High Price': 'High',
        'Low Price': 'Low',
        'Close Price': 'Close'
    }, inplace=True)

    # --- Compute stop levels for each breakout ---
    stops = compute_stop_levels(
        df,
        breakout_lookback=20,
        support_window=10,
        buffer_pct=0.005,
        atr_period=14
    )

    # --- Display results ---
    if stops.empty:
        print("No breakout signals detected with the given parameters.")
    else:
        print("\nSuggested Stops on Breakout Days:\n")
        print(stops.to_string(formatters={
            'Close':      '{:.2f}'.format,
            'Low':        '{:.2f}'.format,
            'Support':    '{:.2f}'.format,
            'ATR':        '{:.2f}'.format,
            'Buffer':     '{:.2f}'.format,
            'StopPrice':  '{:.2f}'.format
        }))

if __name__ == "__main__":
    main()
