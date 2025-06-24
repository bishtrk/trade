#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # 1. Load CSV, handle thousand separators
    df = pd.read_csv('scrip.csv', thousands=',')

    # 2. Clean column names
    df.columns = df.columns.str.strip()

    # 3. Parse 'Date' and set as index
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)

    # 4. Rename Close column
    df = df.rename(columns={'Close Price': 'Close'})

    # 5. Compute 20- and 50-day SMAs
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()

    # 6. Print last few rows with SMAs
    print("\n=== Last 10 entries with SMAs ===")
    print(df[['Close', 'SMA20', 'SMA50']].tail(10), "\n")

    # 7. Plot Close price and SMAs
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close Price')
    plt.plot(df.index, df['SMA20'], label='20-day SMA')
    plt.plot(df.index, df['SMA50'], label='50-day SMA')
    plt.title('TCS Close Price with 20-day & 50-day SMA')
    plt.xlabel('Date')
    plt.ylabel('Price (₹)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
# This script computes and plots the 20-day and 50-day Simple Moving Averages (SMA) for TCS stock.