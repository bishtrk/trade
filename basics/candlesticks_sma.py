#!/usr/bin/env python3
import pandas as pd
import mplfinance as mpf

def main():
    # 1. Load CSV (handle commas in numbers)
    df = pd.read_csv('scrip.csv', thousands=',')
    
    # 2. Clean up column names
    df.columns = df.columns.str.strip()
    
    # 3. Parse dates & set index
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    
    # 4. Rename for mplfinance
    df = df.rename(columns={
        'Open Price':            'Open',
        'High Price':            'High',
        'Low Price':             'Low',
        'Close Price':           'Close',
        'Total Traded Quantity': 'Volume'
    })
    
    # 5. Plot candlestick chart with volume
    mpf.plot(
        df,
        type='candle',
        style='charles',
        title='TCS Candlestick Chart',
        ylabel='Price (₹)',
        volume=True,
        figsize=(12,6),
        mav=(20,50)       # optional: overlay 20 & 50-day SMAs
    )

if __name__ == "__main__":
    main()
