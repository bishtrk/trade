#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

def compute_momentum(df, roc_period=14, rsi_period=14):
    # Rate of Change (ROC)
    df['ROC'] = df['Close'].diff(periods=roc_period) / df['Close'].shift(roc_period) * 100

    # Relative Strength Index (RSI)
    delta = df['Close'].diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=rsi_period, min_periods=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period, min_periods=rsi_period).mean()

    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def main():
    # 1. Load & clean
    df = pd.read_csv('scrip.csv', thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'Close Price':            'Close',
        'Total Traded Quantity':  'Volume'
    }, inplace=True)

    # 2. Compute ROC & RSI
    roc_period = 14
    rsi_period = 14
    df = compute_momentum(df, roc_period, rsi_period)

    # 3. Print last 10 rows of Close, ROC, RSI
    last = df[['Close','ROC','RSI']].tail(10)
    print("\n=== TCS Close, ROC & RSI (last 10 rows) ===")
    print(last.to_string())

    # 4. Plot: top = price+volume, middle = ROC, bottom = RSI
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # --- Price + Volume ---
    ax1.plot(df.index, df['Close'], label='Close Price')
    ax1.set_ylabel('Price (₹)')
    ax1.grid(True)
    ax1.legend(loc='upper left')

    ax1b = ax1.twinx()
    ax1b.bar(df.index, df['Volume'], label='Volume', alpha=0.3)
    ax1b.set_ylabel('Volume')
    ax1b.legend(loc='upper right')

    # --- ROC ---
    ax2.plot(df.index, df['ROC'], label=f'ROC ({roc_period}d)')
    ax2.axhline(0, color='black', linewidth=0.5)
    ax2.set_ylabel('ROC (%)')
    ax2.set_title('Rate of Change')
    ax2.legend()
    ax2.grid(True)

    # --- RSI ---
    ax3.plot(df.index, df['RSI'], label=f'RSI ({rsi_period}d)')
    ax3.axhline(70, color='red', linestyle='--', label='Overbought (70)')
    ax3.axhline(30, color='green', linestyle='--', label='Oversold (30)')
    ax3.set_ylabel('RSI')
    ax3.set_ylim(0, 100)
    ax3.set_title('Relative Strength Index')
    ax3.legend()
    ax3.grid(True)

    # Final touches
    plt.xlabel('Date')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
