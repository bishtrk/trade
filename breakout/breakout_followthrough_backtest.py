#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np

def load_data(path):
    """Load scrip.csv, parse dates, strip commas, rename OHLC columns."""
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'High Price':  'High',
        'Low Price':   'Low',
        'Close Price': 'Close'
    }, inplace=True)
    return df

def detect_price_breakouts(df, price_lookback):
    """Flag days where Close > max(High) of prior price_lookback days."""
    df = df.copy()
    df['Resistance'] = (
        df['High']
          .shift(1)
          .rolling(window=price_lookback, min_periods=1)
          .max()
    )
    df['Breakout'] = df['Close'] > df['Resistance']
    return df

def check_follow_through(df, idx, follow_days, close_near_pct):
    """
    Returns True if on breakout day idx:
      1) Close ≥ Low + close_near_pct*(High−Low)
      2) In the next follow_days, all Closes remain > Resistance level
    """
    res = df.at[idx, 'Resistance']
    high, low, close = df.at[idx, 'High'], df.at[idx, 'Low'], df.at[idx, 'Close']
    # 1) closed in the top (1 − close_near_pct) portion of that bar
    if close < low + close_near_pct * (high - low):
        return False
    # 2) no fallback in the next follow_days bars
    window = df.loc[idx:].iloc[1:follow_days+1]
    if window.empty:
        return False
    return (window['Close'] > res).all()

def backtest_sustain(df, breakout_dates, backtest_days):
    """
    Returns (total, follow_through_count, sustain_count):
    - total breakouts
    - how many had positive follow-through
    - how many were still above breakout Close after backtest_days
    """
    total = 0
    ft_ok = 0
    sustain = 0

    for idx in breakout_dates:
        total += 1
        res = df.at[idx, 'Resistance']
        b_close = df.at[idx, 'Close']

        if check_follow_through(df, idx, args.follow_days, args.close_near_pct):
            ft_ok += 1

        # check N-day later close
        future = df.loc[idx:].iloc[backtest_days:backtest_days+1]
        if not future.empty and future['Close'].iat[0] > b_close:
            sustain += 1

    return total, ft_ok, sustain

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="Breakout + Follow-through + Backtest on TCS")
    p.add_argument('--csv',            default='scrip.csv',    help="Path to scrip.csv")
    p.add_argument('--price-lookback', type=int, default=20, help="Days for resistance lookback")
    p.add_argument('--follow-days',    type=int, default=3,  help="Days to check no-fallback after breakout")
    p.add_argument('--close-near-pct', type=float, default=0.6,
                   help="Close must be in top (1−pct) of candle (e.g. 0.6 = top 40%%)")
    p.add_argument('--backtest-days',  type=int, default=10,
                   help="Days forward to test if Close > breakout Close")
    args = p.parse_args()

    # 1. Load & detect breakouts
    df = load_data(args.csv)
    df = detect_price_breakouts(df, args.price_lookback)
    bo_dates = df.index[df['Breakout']]

    if bo_dates.empty:
        print("No breakouts detected.")
        exit()

    # 2. Compute metrics
    total, ft_ok, sustain = backtest_sustain(
        df, bo_dates, args.backtest_days
    )

    # 3. Print results
    print(f"Total breakouts found: {total}")
    print(f"→ Positive follow-through ({args.follow_days}d, top {int((1-args.close_near_pct)*100)}%): {ft_ok}")
    print(f"→ Sustained after {args.backtest_days} days: {sustain}")
    print(f"Follow-through rate: {ft_ok/total*100:.1f}%")
    print(f"Sustain rate:      {sustain/total*100:.1f}%")

pip install pandas numpy
python breakout_followthrough_backtest.py \
  --csv scrip.csv \
  --price-lookback 20 \
  --follow-days 3 \
  --close-near-pct 0.6 \
  --backtest-days 10
