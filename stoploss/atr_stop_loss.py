#!/usr/bin/env python3
import argparse
import pandas as pd

def compute_atr(df, period=14):
    df = df.copy()
    df['H-L']  = df['High'] - df['Low']
    df['H-PC'] = (df['High'] - df['Close'].shift(1)).abs()
    df['L-PC'] = (df['Low']  - df['Close'].shift(1)).abs()
    tr = df[['H-L','H-PC','L-PC']].max(axis=1)
    return tr.rolling(window=period, min_periods=1).mean()

def load_data(path):
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'Open Price':  'Open',
        'High Price':  'High',
        'Low Price':   'Low',
        'Close Price': 'Close'
    }, inplace=True)
    return df

def main():
    p = argparse.ArgumentParser(description="Compute ATR-based stop loss for TCS.")
    p.add_argument('--entry-date',  required=True, help="Entry date (YYYY-MM-DD)")
    p.add_argument('--entry-price', type=float, required=True, help="Your actual entry price")
    p.add_argument('--multiplier',  type=float, default=2.0,  help="ATR multiplier (e.g. 1.5 or 2.0)")
    args = p.parse_args()

    df = load_data('scrip.csv')
    df['ATR'] = compute_atr(df, period=14)

    entry_date  = pd.to_datetime(args.entry_date)
    if entry_date not in df.index:
        raise ValueError(f"Entry date {entry_date.date()} not found in data.")

    atr_value    = df.at[entry_date, 'ATR']
    stop_loss    = args.entry_price - args.multiplier * atr_value

    print(f"Entry Date : {entry_date.date()}")
    print(f"Entry Price: ₹{args.entry_price:.2f}")
    print(f"ATR (14d)  : ₹{atr_value:.2f}")
    print(f"Multiplier : {args.multiplier}×ATR")
    print(f"Stop Loss  : ₹{stop_loss:.2f}")

if __name__ == '__main__':
    main()
