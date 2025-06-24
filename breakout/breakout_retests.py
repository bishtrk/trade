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
        'Close Price': 'Close'
    }, inplace=True)
    return df

def detect_breakouts(df, lookback):
    df = df.copy()
    df['Resistance'] = (
        df['High']
          .shift(1)
          .rolling(window=lookback, min_periods=1)
          .max()
    )
    df['Breakout'] = df['Close'] > df['Resistance']
    return df

def check_follow_through(df, idx, pct=0.6):
    """Optional: ensure breakout candle closes in the top (1−pct) of its range."""
    low, high, close = df.at[idx, ['Low','High','Close']]
    return close >= low + pct * (high - low)

def find_retests(df, breakout_dates, buffer_pct, lookahead, require_ft):
    """
    For each breakout date:
      - If require_ft: skip if no follow-through
      - Look ahead up to `lookahead` days
      - Retest occurs when Low <= Resistance*(1+buffer_pct) and Close > Resistance
    """
    retests = []
    for dt in breakout_dates:
        res = df.at[dt, 'Resistance']
        if pd.isna(res): 
            continue
        # optional follow-through check
        if require_ft and not check_follow_through(df, dt):
            continue
        threshold = res * (1 + buffer_pct)
        window = df.loc[dt:].iloc[1:lookahead+1]  # next bars
        for d, row in window.iterrows():
            if row['Low'] <= threshold and row['Close'] > res:
                retests.append({
                    'Breakout Date': dt,
                    'Retest Date': d,
                    'Resistance': res,
                    'Retest Low': row['Low'],
                    'Retest Close': row['Close']
                })
                break
    return pd.DataFrame(retests)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="Detect breakout retests on TCS")
    p.add_argument('--csv',              default='scrip.csv',help="Path to CSV")
    p.add_argument('--price-lookback',   type=int, default=20, help="Days for prior resistance")
    p.add_argument('--retest-buffer-pct',type=float, default=0.005,
                   help="Allow Low ≤ Resistance*(1+this buffer)")
    p.add_argument('--retest-lookahead', type=int, default=5,
                   help="Max days after breakout to look for a retest")
    p.add_argument('--require-followthrough', action='store_true',
                   help="Only consider breakouts whose candle closed strong (top 40%)")
    args = p.parse_args()

    df = load_data(args.csv)
    df = detect_breakouts(df, args.price_lookback)
    bo_dates = df.index[df['Breakout']]

    retest_df = find_retests(
        df,
        bo_dates,
        buffer_pct=args.retest_buffer_pct,
        lookahead=args.retest_lookahead,
        require_ft=args.require_followthrough
    )

    if retest_df.empty:
        print("No retests found.")
    else:
        pd.set_option('display.float_format','{:.2f}'.format)
        print("\nRetest Entries Detected:\n")
        print(retest_df[['Breakout Date','Retest Date','Resistance','Retest Low','Retest Close']])

pip install pandas numpy
python breakout_retest.py \
  --csv scrip.csv \
  --price-lookback 20 \
  --retest-buffer-pct 0.005 \
  --retest-lookahead 5 \
  --require-followthrough
