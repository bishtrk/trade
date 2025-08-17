#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def load_data(path):
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'High Price':            'High',
        'Low Price':             'Low',
        'Open Price':            'Open',
        'Close Price':           'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)
    # Drop duplicate dates to ensure unique index
    df = df[~df.index.duplicated(keep='first')]
    return df


def compute_atr(df, period):
    hl = df['High'] - df['Low']
    hc = (df['High'] - df['Close'].shift(1)).abs()
    lc = (df['Low']  - df['Close'].shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=1).mean()


def detect_dynamic_breakouts(df, mode, atr_period, multiplier):
    df = df.copy()
    df['ATR'] = compute_atr(df, atr_period)
    if mode == 'range':
        df['Move'] = df['High'] - df['Low']
    else:
        df['Move'] = (df['Close'] - df['Open']).abs()
    df['Breakout_ATR'] = df['Move'] > multiplier * df['ATR']
    return df


def safe_close(df, dt):
    """Return a scalar close for date dt, even if index was duplicated."""
    val = df.loc[dt, 'Close']
    if isinstance(val, pd.Series):
        return float(val.iloc[0])
    return float(val)


def plot_breakouts(df, bo_dates, args):
    fig, ax_price = plt.subplots(figsize=(12, 6))
    # price line
    ax_price.plot(df.index, df['Close'], label='Close Price', linewidth=1.2)
    # breakout markers
    y = [safe_close(df, dt) for dt in bo_dates]
    ax_price.scatter(bo_dates, y, marker='o', color='red', label='ATR Breakout', zorder=5)
    ax_price.set_ylabel('Price')
    ax_price.legend(loc='upper left')

    # volume bars on twin axis
    ax_vol = ax_price.twinx()
    ax_vol.bar(df.index, df['Volume'], width=1, alpha=0.3, label='Volume')
    ax_vol.set_ylabel('Volume')

    title = (f"ATR Breakouts (mode={args.mode}, atr={args.atr_period}, "
             f"mult={args.multiplier})")
    ax_price.set_title(title)
    plt.tight_layout()
    plt.show()


def main():
    p = argparse.ArgumentParser(description="ATR-Based Dynamic Breakout Detector with Chart")
    p.add_argument('--csv',         default='scrip.csv', help="Path to data CSV")
    p.add_argument('--mode',        choices=['range','net'], default='range',
                   help="Use High–Low ('range') or |Close–Open| ('net') for Move")
    p.add_argument('--atr-period',  type=int, default=14, help="ATR look-back period")
    p.add_argument('--multiplier',  type=float, default=2.0, help="ATR multiple for breakout")
    args = p.parse_args()

    df = load_data(args.csv)
    df = detect_dynamic_breakouts(df, args.mode, args.atr_period, args.multiplier)
    bo = df[df['Breakout_ATR']]
    if bo.empty:
        print("No ATR-based dynamic breakouts found.")
    else:
        pd.set_option('display.float_format', '{:.2f}'.format)
        print(f"\nATR-Based Breakouts (mode={args.mode}, atr={args.atr_period}, mult={args.multiplier}):\n")
        print(bo[['High','Low','Open','Close','Move','ATR']].to_string())
        plot_breakouts(df, bo.index.tolist(), args)

if __name__ == '__main__':
    main()
