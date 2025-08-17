#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
import mplfinance as mpf

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
    return df

def compute_rsi(close, period=14):
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.ewm(com=period-1, adjust=False).mean()
    ma_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))

def compute_stoch(high, low, close, k_period=14, d_period=3):
    low_min  = low.rolling(k_period, min_periods=1).min()
    high_max = high.rolling(k_period, min_periods=1).max()
    k = (close - low_min) / (high_max - low_min) * 100
    d = k.rolling(d_period, min_periods=1).mean()
    return k, d

def compute_macd(close, fast=12, slow=26, signal=9):
    ema_fast  = close.ewm(span=fast, adjust=False).mean()
    ema_slow  = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    sig_line  = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - sig_line
    return macd_line, sig_line, hist

def main():
    p = argparse.ArgumentParser(description="Overbought Breakout Chart Without pandas_ta")
    p.add_argument('--csv', default='scrip.csv', help="Path to CSV file")
    args = p.parse_args()

    df = load_data(args.csv)

    # 1) Indicators
    df['SMA20'] = df['Close'].rolling(20).mean()
    df['RSI14'] = compute_rsi(df['Close'], 14)
    df['STOCHK'], df['STOCHD'] = compute_stoch(df['High'], df['Low'], df['Close'], 14, 3)
    df['MACD'], df['MACD_SIGNAL'], df['MACD_HIST'] = compute_macd(df['Close'], 12, 26, 9)

    # 2) Breakout logic
    df['Resistance20'] = df['High'].shift(1).rolling(20, min_periods=1).max()
    df['Breakout'] = df['Close'] > df['Resistance20']
    df['OverboughtBreakout'] = (
        df['Breakout'] &
        ((df['RSI14'] > 70) | (df['STOCHK'] > 80) | (df['STOCHD'] > 80))
    )

    # 3) Build mplfinance addplots
    apds = [
        mpf.make_addplot(df['SMA20'], color='blue'),
        mpf.make_addplot(
            df['Close'].where(df['OverboughtBreakout']),
            type='scatter', marker='^', markersize=100, color='red'
        ),
        mpf.make_addplot(df['RSI14'], panel=1, ylabel='RSI14'),
        mpf.make_addplot(pd.Series(70, index=df.index), panel=1,
                         color='gray', linestyle='--'),
        mpf.make_addplot(df['STOCHK'], panel=2, ylabel='STOCHK'),
        mpf.make_addplot(df['STOCHD'], panel=2, color='orange'),
        # fixed: separate reference lines for Stochastic
        mpf.make_addplot(pd.Series(80, index=df.index), panel=2,
                         color='gray', linestyle='--'),
        mpf.make_addplot(pd.Series(20, index=df.index), panel=2,
                         color='gray', linestyle='--'),
        mpf.make_addplot(df['MACD'], panel=3, ylabel='MACD'),
        mpf.make_addplot(df['MACD_SIGNAL'], panel=3, color='orange'),
        mpf.make_addplot(df['MACD_HIST'], panel=3, type='bar', width=0.7, alpha=0.5),
    ]

    # 4) Plot
    mpf.plot(
        df,
        type='candle',
        style='charles',
        volume=True,
        addplot=apds,
        figratio=(16,9),
        figscale=1.2,
        panel_ratios=(6,2,2,2),
        title='Overbought Breakouts & Indicators',
        tight_layout=True
    )

if __name__ == '__main__':
    main()
