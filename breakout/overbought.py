#!/usr/bin/env python3
import pandas as pd
import pandas_ta as ta
import mplfinance as mpf
import numpy as np

# 1. Load & prepare data
df = pd.read_csv('scrip.csv', thousands=',')
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

# 2. Compute SMA
df['SMA20'] = df['Close'].rolling(20).mean()

# 3. Compute breakout signal
df['Resistance20'] = df['High'].shift(1).rolling(20).max()
df['Breakout'] = df['Close'] > df['Resistance20']

# 4. Compute indicators
df['RSI14'] = ta.rsi(df['Close'], length=14)
stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
df[['STOCHK','STOCHD']] = stoch[['STOCHk_14_3_3','STOCHd_14_3_3']]
macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
df[['MACD','MACD_SIGNAL','MACD_HIST']] = macd[['MACD_12_26_9','MACDs_12_26_9','MACDh_12_26_9']]

# 5. Flag overbought breakouts
df['OverboughtBreakout'] = (
    df['Breakout'] &
    (
      (df['RSI14']   > 70) |
      (df['STOCHK']  > 80) |
      (df['STOCHD']  > 80)
    )
)

# 6. Prepare mplfinance panels
# Price + SMA + breakout markers
price_apds = [
    mpf.make_addplot(df['SMA20'], color='blue', width=1),
    mpf.make_addplot(
        df['Close'].where(df['OverboughtBreakout']),
        type='scatter', marker='^', markersize=100, color='red'
    )
]

# RSI panel
rsi_apd = mpf.make_addplot(df['RSI14'], panel=1, ylabel='RSI')
rsi_signal = mpf.make_addplot(
    pd.Series(70, index=df.index), panel=1, color='gray', linestyle='--'
)

# Stochastic panel
sto_apd_k = mpf.make_addplot(df['STOCHK'], panel=2, ylabel='Stoch')
sto_apd_d = mpf.make_addplot(df['STOCHD'], panel=2, color='orange')
sto_signal = mpf.make_addplot(
    pd.Series([80,20], index=df.index).T,
    panel=2, color='gray', linestyle='--'
)

# MACD panel
macd_apd = mpf.make_addplot(df['MACD'],      panel=3, ylabel='MACD')
signal_apd = mpf.make_addplot(df['MACD_SIGNAL'], panel=3, color='orange')
hist_apd   = mpf.make_addplot(df['MACD_HIST'],   panel=3, type='bar', width=0.7, alpha=0.5)

all_apds = price_apds + [rsi_apd, rsi_signal, sto_apd_k, sto_apd_d, sto_signal, macd_apd, signal_apd, hist_apd]

# 7. Plot
mpf.plot(
    df,
    type='candle',
    style='charles',
    volume=True,
    addplot=all_apds,
    figratio=(16,9),
    figscale=1.2,
    panel_ratios=(6,2,2,2),
    title='TCS: Price+SMA20 with Overbought Breakouts & Indicators',
    tight_layout=True
)
