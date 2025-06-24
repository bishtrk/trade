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

    # Simple moving averages of gains and losses
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
    df.rename(columns={'Close Price': 'Close'}, inplace=True)

    # 2. Compute ROC & RSI
    roc_period = 14
    rsi_period = 14
    df = compute_momentum(df, roc_period, rsi_period)

    # 3. Output the last 10 values
    print("\n=== TCS ROC & RSI (last 10 rows) ===")
    print(df[['ROC','RSI']].tail(10))

    # 4. Plot both indicators
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # ROC plot
    ax1.plot(df.index, df['ROC'], label=f'ROC ({roc_period}d)')
    ax1.axhline(0, color='black', linewidth=0.5)
    ax1.set_title('Rate of Change (ROC)')
    ax1.set_ylabel('ROC (%)')
    ax1.legend()
    ax1.grid(True)

    # RSI plot
    ax2.plot(df.index, df['RSI'], label=f'RSI ({rsi_period}d)')
    ax2.axhline(70, color='red', linestyle='--', label='Overbought (70)')
    ax2.axhline(30, color='green', linestyle='--', label='Oversold (30)')
    ax2.set_title('Relative Strength Index (RSI)')
    ax2.set_ylabel('RSI')
    ax2.set_ylim(0, 100)
    ax2.legend()
    ax2.grid(True)

    plt.xlabel('Date')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
