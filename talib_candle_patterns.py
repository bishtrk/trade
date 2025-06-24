#!/usr/bin/env python3
import pandas as pd
import numpy as np
import talib
import mplfinance as mpf

def main():
    # 1. Load & prepare data
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

    # 2. Call TA-Lib pattern functions
    patterns = {
        'Doji':            talib.CDLDOJI,
        'Hammer':          talib.CDLHAMMER,
        'Inverted Hammer': talib.CDLINVERTEDHAMMER,
        'Spinning Top':    talib.CDLSPINNINGTOP,
        'Dragonfly Doji':  talib.CDLDRAGONFLYDOJI,
        'Gravestone Doji': talib.CDLGRAVESTONEDOJI,
        'Engulfing':       talib.CDLENGULFING,
    }

    signals = pd.DataFrame(index=df.index)
    for name, func in patterns.items():
        # TA-Lib returns +100 for bullish, −100 for bearish, 0 for none
        sig = func(df['Open'], df['High'], df['Low'], df['Close'])
        # Keep only non-zero signals
        signals[name] = np.where(sig != 0, sig, np.nan)

    # 3. Prepare OHLCV DataFrame
    ohlcv = df[['Open','High','Low','Close','Volume']].copy()

    # 4. Build addplots for each pattern
    apds = []
    # assign a distinct marker/color per pattern
    marker_map = {
        'Doji':            ('o','b'),
        'Hammer':          ('^','g'),
        'Inverted Hammer': ('v','r'),
        'Spinning Top':    ('s','m'),
        'Dragonfly Doji':  ('D','c'),
        'Gravestone Doji': ('X','k'),
        'Engulfing':       ('P','y'),
    }
    for name, series in signals.items():
        marker, color = marker_map[name]
        # price to plot markers at
        price = df['Close'] * (1 + (0.02 if series>0 else -0.02))
        # mask non-signals
        price = price.where(~np.isnan(series))
        apds.append(
            mpf.make_addplot(
                price,
                type='scatter',
                marker=marker,
                markersize=100,
                color=color,
                panel=0
            )
        )

    # 5. Plot everything
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
