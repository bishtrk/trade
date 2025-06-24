#!/usr/bin/env python3
import pandas as pd
import mplfinance as mpf

def main():
    # 1. Load CSV, handle thousand separators
    df = pd.read_csv('scrip.csv', thousands=',')
    
    # 2. Clean column names
    df.columns = df.columns.str.strip()
    
    # 3. Parse 'Date' and set as index
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    
    # 4. Rename for mplfinance (OHLC + Volume)
    df = df.rename(columns={
        'Open Price':              'Open',
        'High Price':              'High',
        'Low Price':               'Low',
        'Close Price':             'Close',
        'Total Traded Quantity':   'Volume'
    })
    
    # 5. Prepare DataFrame with OHLCV
    ohlcv = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    
    # 6. Plot candlestick chart with volume
    mpf.plot(
        ohlcv,
        type='candle',
        style='charles',
        title='TCS Candlestick Chart with Volume',
        ylabel='Price (₹)',
        volume=True,
        figsize=(12, 6)
    )

if __name__ == "__main__":
    main()
