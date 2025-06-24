#!/usr/bin/env python3
import pandas as pd

def compute_atr(df, period=14):
    """
    Compute the Average True Range (ATR) over the given period.
    """
    high_low = df['High'] - df['Low']
    high_prev_close = (df['High'] - df['Close'].shift(1)).abs()
    low_prev_close  = (df['Low'] - df['Close'].shift(1)).abs()
    tr = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=1).mean()
    return atr

def main():
    # 1. Load and prepare data
    df = pd.read_csv('scrip.csv', thousands=',')
    # Strip whitespace
    df.columns = df.columns.str.strip()
    # Rename columns for simplicity
    df.rename(columns={
        'High Price': 'High',
        'Low Price': 'Low',
        'Close Price': 'Close'
    }, inplace=True)
    # Parse dates and set index
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    
    # 2. Compute ATR (14-day by default)
    atr_period = 14
    df['ATR'] = compute_atr(df, period=atr_period)
    
    # 3. Set your entry parameters
    entry_date_str = '2025-06-20'    # change to your entry date
    entry_price    = 3435.70         # change to the price you paid
    k              = 1.5             # ATR multiplier (e.g., 1.0–1.5)
    
    entry_date = pd.to_datetime(entry_date_str)
    
    # 4. Fetch ATR at entry
    if entry_date not in df.index:
        raise ValueError(f"Entry date {entry_date_str} not found in data index.")
    atr_at_entry = df.at[entry_date, 'ATR']
    
    # 5. Calculate initial stop
    stop_price = entry_price - k * atr_at_entry
    
    # 6. Display results
    print(f"Entry Date        : {entry_date.date()}")
    print(f"Entry Price       : ₹{entry_price:.2f}")
    print(f"ATR ({atr_period}d)      : {atr_at_entry:.2f}")
    print(f"ATR Multiplier (k): {k}")
    print(f"Initial Stop Loss : ₹{stop_price:.2f}")

if __name__ == '__main__':
    main()
