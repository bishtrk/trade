#!/usr/bin/env python3
import pandas as pd
import numpy as np
import mplfinance as mpf

def detect_single_candle_patterns(df):
    # Calculate body and shadows
    df['body']         = df['Close'] - df['Open']
    df['body_size']    = df['body'].abs()
    df['candle_range'] = df['High'] - df['Low']
    df['upper_shadow'] = df['High'] - df[['Open','Close']].max(axis=1)
    df['lower_shadow'] = df[['Open','Close']].min(axis=1) - df['Low']

    # Thresholds
    small_body_thresh = 0.1   # 10% of range
    long_shadow_ratio = 2.0   # 2× body size

    # Doji types
    doji       = df['body_size'] <= df['candle_range'] * small_body_thresh
    dragonfly  = doji & (df['upper_shadow'] <= df['candle_range']*small_body_thresh) \
                   & (df['lower_shadow'] >= df['candle_range']*0.6)
    gravestone = doji & (df['lower_shadow'] <= df['candle_range']*small_body_thresh) \
                   & (df['upper_shadow'] >= df['candle_range']*0.6)
    standard   = doji & ~dragonfly & ~gravestone

    # Hammer & Inverted Hammer (bullish)
    hammer     = (df['body_size'] > 0) \
                 & (df['lower_shadow'] >= df['body_size']*long_shadow_ratio) \
                 & (df['upper_shadow'] <= df['body_size']*0.5) \
                 & (df['Close'] > df['Open'])
    inv_hammer = (df['body_size'] > 0) \
                 & (df['upper_shadow'] >= df['body_size']*long_shadow_ratio) \
                 & (df['lower_shadow'] <= df['body_size']*0.5) \
                 & (df['Close'] > df['Open'])

    # Spinning Top
    spinning_top = (df['body_size'] <= df['candle_range']*0.25) \
                   & (df['upper_shadow'] >= df['body_size']*long_shadow_ratio) \
                   & (df['lower_shadow'] >= df['body_size']*long_shadow_ratio)

    # Assign pattern names
    df['Pattern'] = ''
    df.loc[standard,        'Pattern'] = 'Doji'
    df.loc[dragonfly,       'Pattern'] = 'Dragonfly Doji'
    df.loc[gravestone,      'Pattern'] = 'Gravestone Doji'
    df.loc[hammer,          'Pattern'] = 'Hammer'
    df.loc[inv_hammer,      'Pattern'] = 'Inverted Hammer'
    df.loc[spinning_top,    'Pattern'] = 'Spinning Top'
    return df

def plot_with_patterns(df):
    # Masked marker series
    buy_markers  = df['Pattern'].isin(['Hammer','Dragonfly Doji'])
    sell_markers = df['Pattern'].isin(['Inverted Hammer','Gravestone Doji'])
    neutral_markers = df['Pattern'].isin(['Doji','Spinning Top'])

    buy_series    = df['Low'] * 0.995
    sell_series   = df['High'] * 1.005
    neutral_series= df['Close']

    buy_series[~buy_markers]       = np.nan
    sell_series[~sell_markers]     = np.nan
    neutral_series[~neutral_markers]= np.nan

    apds = [
        mpf.make_addplot(buy_series,     type='scatter', marker='^', markersize=80, color='g'),
        mpf.make_addplot(sell_series,    type='scatter', marker='v', markersize=80, color='r'),
        mpf.make_addplot(neutral_series, type='scatter', marker='o', markersize=50, color='b'),
    ]

    mpf.plot(
        df,
        type='candle',
        style='charles',
        title='TCS Single-Candle Patterns',
        volume=True,
        addplot=apds,
        figsize=(12,6),
        ylabel='Price (₹)'
    )

def main():
    # --- LOAD & CLEAN ---
    df = pd.read_csv('scrip.csv', thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)

    df.rename(columns={
        'Open Price':            'Open',
        'High Price':            'High',
        'Low Price':             'Low',
        'Close Price':           'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)

    for col in ['Open','High','Low','Close','Volume']:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found. Available: {df.columns.tolist()}")

    # --- DETECT & PLOT ---
    df = detect_single_candle_patterns(df)
    print("Detected patterns:\n", df.loc[df['Pattern']!='', ['Open','High','Low','Close','Pattern']])
    plot_with_patterns(df)

if __name__ == "__main__":
    main()
