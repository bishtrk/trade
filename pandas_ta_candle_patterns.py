#!/usr/bin/env python3
import numpy as np
# patch for pandas_ta expecting numpy.NaN
np.NaN = np.nan

import pandas as pd
import mplfinance as mpf
import pandas_ta as ta

def main():
    # 1. Load & prep your TCS data
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

    # 2. Detect candlestick patterns via pandas_ta cdl_pattern
    patterns = [
        "doji",
        "hammer",
        "inverted_hammer",
        "spinning_top",
        "dragonfly_doji",
        "gravestone_doji",
        "engulfing"
    ]
    # this appends one column per pattern, values ±100 on signal, else NaN
    df.ta.cdl_pattern(name=patterns, append=True)

    # 3. Prepare a clean OHLCV DataFrame
    ohlcv = df[['Open','High','Low','Close','Volume']].copy()

    # 4. Build marker addplots for each pattern
    marker_map = {
        'CDLDOJI':           ('o','b'),
        'CDLHAMMER':         ('^','g'),
        'CDLINVERTEDHAMMER': ('v','r'),
        'CDLSPINNINGTOP':    ('s','m'),
        'CDLDRAGONFLYDOJI':  ('D','c'),
        'CDLGRAVESTONEDOJI': ('X','k'),
        'CDLENGULFING':      ('P','y'),
    }
    apds = []
    for col, (marker, color) in marker_map.items():
        if col not in df.columns:
            continue
        sig = df[col].replace({0: np.nan})
        # offset above/below the close for visibility
        offsets = np.where(sig > 0, 1.02, 0.98)
        price = df['Close'] * offsets
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
        title='TCS Candlestick Patterns (pandas_ta)',
        volume=True,
        addplot=apds,
        figsize=(14,8),
        ylabel='Price (₹)'
    )

if __name__ == '__main__':
    main()
