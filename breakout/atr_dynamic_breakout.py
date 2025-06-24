#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np

def load_data(path):
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'High Price':  'High',
        'Low Price':   'Low',
        'Open Price':  'Open',
        'Close Price': 'Close'
    }, inplace=True)
    return df

def compute_atr(df, period):
    """Compute N-day ATR (Average True Range)."""
    hl = df['High'] - df['Low']
    hc = (df['High'] - df['Close'].shift(1)).abs()
    lc = (df['Low']  - df['Close'].shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=1).mean()

def detect_dynamic_breakouts(df, mode, atr_period, multiplier):
    df['ATR'] = compute_atr(df, atr_period)
    if mode == 'range':
        df['Move'] = df['High'] - df['Low']
    else:  # 'net'
        df['Move'] = (df['Close'] - df['Open']).abs()
    df['Breakout_ATR'] = df['Move'] > multiplier * df['ATR']
    return df

def main():
    p = argparse.ArgumentParser(description="ATR-Based Dynamic Breakout Detector")
    p.add_argument('--csv',         default='scrip.csv',    help="Path to scrip.csv")
    p.add_argument('--mode',        choices=['range','net'], default='range',
                   help="Compare ATR to High–Low ('range') or |Close–Open| ('net')")
    p.add_argument('--atr-period',  type=int, default=14,    help="ATR look-back period")
    p.add_argument('--multiplier',  type=float, default=2.0, help="ATR multiple for breakout")
    args = p.parse_args()

    df = load_data(args.csv)
    df = detect_dynamic_breakouts(df, args.mode, args.atr_period, args.multiplier)

    bo = df[df['Breakout_ATR']]
    if bo.empty:
        print("No ATR-based dynamic breakouts found.")
    else:
        pd.set_option('display.float_format', '{:.2f}'.format)
        print(f"ATR-Based Breakouts (mode={args.mode}, atr={args.atr_period}, mult={args.multiplier}):\n")
        print(bo[['High','Low','Open','Close','Move','ATR']].to_string())

if __name__ == '__main__':
    main()

#python atr_dynamic_breakout.py --mode range --atr-period 14 --multiplier 2.0
