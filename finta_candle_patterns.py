#!/usr/bin/env python3
import pandas as pd
import numpy as np
import mplfinance as mpf
from finta import TA

def main():
    # 1. Load & clean
    df = pd.read_csv('scrip.csv', thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    
    # Finta expects lowercase OHLCV
    df.rename(columns={
        'Open Price':            'open',
        'High Price':            'high',
        'Low Price':             'low',
        'Close Price':           'close',
        'Total Traded Quantity': 'volume'
    }, inplace=True)
    
    # 2. Detect patterns with Finta
    # Returns +1 for bullish pattern, -1 for bearish, 0 if none
    df['doji']            = TA.CDL_DOJI(df)
    df['hammer']          = TA.CDL_HAMMER(df)
    df['inverted_hammer'] = TA.CDL_INVERTED_HAMMER(df)
    df['engulfing']       = TA.CDL_ENGULFING(df)
    
    # 3. Prepare OHLCV for plotting
    ohlcv = df[['open','high','low','close','volume']]
    
    # 4. Build addplots for each pattern
    apds = []
    marker_map = {
        'doji':            ('o','b'),
        'hammer':          ('^','g'),
        'inverted_hammer': ('v','r'),
        'engulfing':       ('P','y'),
    }
    for pat, (marker, color) in marker_map.items():
        sig = df[pat].replace({0: np.nan})
        # offset price ±2% so markers are visible
        price = df['close'] * (1 + 0.02*np.sign(sig))
        price[sig.isna()] = np.nan
        apds.append(
            mpf.make_addplot(
                price,
                type='scatter',
                marker=marker,
                markersize=100,
                color=color
            )
        )
    
    # 5. Plot candlesticks + volume + pattern markers
    mpf.plot(
        ohlcv,
        type='candle',
        style='charles',
        title='TCS Candlestick Patterns (Finta)',
        volume=True,
        addplot=apds,
        figsize=(14,8),
        ylabel='Price (₹)'
    )

if __name__ == '__main__':
    main()
