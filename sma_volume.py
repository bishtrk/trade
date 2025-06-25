#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # 1. Load CSV, handle thousands separators
    df = pd.read_csv('scrip.csv', thousands=',')
    df.columns = df.columns.str.strip()

    # 2. Parse 'Date' and set as index
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)

    # 3. Rename columns
    df.rename(columns={
        'Close Price': 'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)

    # 4. Compute 20- and 50-day SMAs
    df['SMA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
    df['SMA50'] = df['Close'].rolling(window=50, min_periods=1).mean()

    # 5. Print last 10 rows with Close and SMAs
    print("\n=== Last 10 entries with Close, SMA20 & SMA50 ===")
    print(df[['Close', 'SMA20', 'SMA50']].tail(10), "\n")

    # 6. Plot Close, SMAs and Volume on the same chart
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot price and SMAs
    ax1.plot(df.index, df['Close'],  label='Close Price')
    ax1.plot(df.index, df['SMA20'],  label='20-day SMA')
    ax1.plot(df.index, df['SMA50'],  label='50-day SMA')
    ax1.set_ylabel('Price (₹)')
    ax1.legend(loc='upper left')
    ax1.grid(True)

    # Twin axis for volume
    ax2 = ax1.twinx()
    ax2.bar(df.index, df['Volume'], label='Volume', alpha=0.3, width=1.0)
    ax2.set_ylabel('Volume')
    ax2.legend(loc='upper right')

    # Final formatting
    plt.title('Stock Close Price, 20/50-day SMAs and Volume')
    plt.xlabel('Date')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
