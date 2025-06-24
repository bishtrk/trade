#!/usr/bin/env python3
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

def load_data(path):
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'Open Price': 'Open',
        'High Price': 'High',
        'Low Price': 'Low',
        'Close Price': 'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)
    return df

def recent_swing_low(df, entry_date, lookback=20, order=2):
    # look at the N days before entry_date
    window = df.loc[:entry_date].iloc[-lookback-1:-1]
    lows = window['Low']
    # local minima: low[i] <= neighbors ±order
    idx = argrelextrema(lows.values, np.less_equal, order=order)[0]
    if len(idx)==0:
        return None
    swing = lows.iloc[idx]
    # pick the most recent one
    return swing.iloc[-1]

def moving_emas(df, entry_date):
    ema20 = df['Close'].ewm(span=20, adjust=False).mean().loc[entry_date]
    ema50 = df['Close'].ewm(span=50, adjust=False).mean().loc[entry_date]
    return ema20, ema50

def previous_resistance(df, entry_date, window=20):
    return df['High'].rolling(window=window).max().shift(1).loc[entry_date]

def main():
    df = load_data('scrip.csv')
    entry_date  = df.index[-1]
    entry_price = df.at[entry_date, 'Close']
    print(f"Entry Date: {entry_date.date()}, Entry Price: ₹{entry_price:.2f}\n")

    # 1) Recent Swing Low
    swing_low = recent_swing_low(df, entry_date, lookback=20, order=2)
    print(f"Recent Swing Low: ₹{swing_low:.2f}" if swing_low is not None else "No swing low found")

    # 2) Key EMAs
    ema20, ema50 = moving_emas(df, entry_date)
    print(f"20-EMA:        ₹{ema20:.2f}")
    print(f"50-EMA:        ₹ema50:.2f\n".replace('₹ema50', f'{ema50:.2f}'))

    # 3) Previous Resistance → Support
    prev_res = previous_resistance(df, entry_date, window=20)
    print(f"Previous Resistance (as Support): ₹{prev_res:.2f}\n")

    # Combine supports below entry
    levels = []
    if swing_low is not None: levels.append(swing_low)
    levels += [ema20, ema50, prev_res]
    candidates = [lvl for lvl in levels if lvl < entry_price]
    if not candidates:
        print("No support level found below entry price.")
        return

    nearest_support = max(candidates)
    print(f"Nearest Support Level: ₹{nearest_support:.2f}")

    # Buffer and final stop
    buffer_pct = 0.02  # 2% below support
    stop = nearest_support * (1 - buffer_pct)
    print(f"Suggested Stop-Loss (2% buffer): ₹{stop:.2f}")

if __name__ == '__main__':
    main()
