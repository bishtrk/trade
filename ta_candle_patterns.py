#!/usr/bin/env python3
import pandas as pd
import numpy as np
import mplfinance as mpf
import talib as ta  # Changed from finta to talib

def main():
    # 1. Load & clean
    df = pd.read_csv('scrip.csv', thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    
    # TA-Lib expects specific column names (can be uppercase)
    df.rename(columns={
        'Open Price':            'Open',
        'High Price':            'High', 
        'Low Price':             'Low',
        'Close Price':           'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)
    
    # 2. Detect patterns with TA-Lib
    # Returns non-zero values for pattern detection
    df['doji'] = ta.CDLDOJI(df['Open'], df['High'], df['Low'], df['Close'])
    df['hammer'] = ta.CDLHAMMER(df['Open'], df['High'], df['Low'], df['Close'])
    df['inverted_hammer'] = ta.CDLINVERTEDHAMMER(df['Open'], df['High'], df['Low'], df['Close'])
    df['engulfing'] = ta.CDLENGULFING(df['Open'], df['High'], df['Low'], df['Close'])
    
    # 3. Prepare OHLCV for plotting (mplfinance expects lowercase)
    ohlcv = df[['Open','High','Low','Close','Volume']].copy()
    ohlcv.columns = ['open', 'high', 'low', 'close', 'volume']
    
    # 4. Build addplots for each pattern
    apds = []
    marker_map = {
        'doji':            ('o','b'),
        'hammer':          ('^','g'),
        'inverted_hammer': ('v','r'),
        'engulfing':       ('P','y'),
    }
    
    for pat, (marker, color) in marker_map.items():
        # TA-Lib returns 0 for no pattern, non-zero for pattern
        sig = df[pat].replace({0: np.nan})
        # Convert non-zero values to +1 or -1 for positioning
        sig = np.sign(sig)
        
        # offset price ±2% so markers are visible
        price = df['Close'] * (1 + 0.02 * sig)
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
        title='TCS Candlestick Patterns (TA-Lib)',
        volume=True,
        addplot=apds,
        figsize=(14,8),
        ylabel='Price (₹)'
    )

if __name__ == '__main__':
    main()