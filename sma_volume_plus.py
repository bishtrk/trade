#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compute_rsi(series, period=14):
    """Compute RSI given a price series."""
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    # first average
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    # smooth with Wilder’s
    avg_gain = avg_gain.shift(1).ewm(alpha=1/period, adjust=False).mean()
    avg_loss = avg_loss.shift(1).ewm(alpha=1/period, adjust=False).mean()
    rs  = avg_gain / avg_loss
    rsi = 100 - (100/(1+rs))
    return rsi

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

    # 5. Compute RSI & MACD
    df['RSI'] = compute_rsi(df['Close'], period=14)
    df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # 6. Identify local swing-lows (simple 1-day lookback/look-ahead)
    df['SwingLow'] = (
        (df['Close'].shift(1) > df['Close']) &
        (df['Close'].shift(-1) > df['Close'])
    )

    # 7. Flag heavy down-volume days
    vol20 = df['Volume'].rolling(window=20, min_periods=1).mean()
    df['HeavyDownVol'] = (df['Volume'] > vol20 * 1.5) & (df['Close'] < df['Close'].shift(1))

    # 8. Print swing-lows and heavy down-volume triggers
    print("=== Swing-Low points ===")
    print(df.loc[df['SwingLow'], ['Close']], "\n")
    print("=== Heavy down-volume days ===")
    print(df.loc[df['HeavyDownVol'], ['Close','Volume']], "\n")

    # 9. Plot everything
    fig, (ax0, ax1, ax2) = plt.subplots(
        nrows=3, ncols=1, sharex=True,
        figsize=(14,10),
        gridspec_kw={'height_ratios': [3,1,1]}
    )

    # --- Top panel: Price, SMAs, swing-lows, volume bars ---
    ax0.plot(df.index, df['Close'], label='Close Price', lw=1)
    ax0.plot(df.index, df['SMA20'], label='20-day SMA',  lw=1)
    ax0.plot(df.index, df['SMA50'], label='50-day SMA',  lw=1)
    # Mark swing-lows
    swings = df[df['SwingLow']]
    ax0.scatter(swings.index, swings['Close'],
                marker='v', color='purple', s=100, label='Swing Low')
    # Volume on twin-axis, coloring heavy down-vol red
    ax0_vol = ax0.twinx()
    colors = np.where(df['HeavyDownVol'], 'red', 'lightblue')
    ax0_vol.bar(df.index, df['Volume'],
                width=1.0, alpha=0.4, color=colors, label='Volume')
    ax0.set_ylabel('Price (₹)')
    ax0_vol.set_ylabel('Volume')
    ax0.legend(loc='upper left')
    ax0_vol.legend(loc='upper right')
    ax0.grid(True)

    # --- Middle panel: RSI(14) ---
    ax1.plot(df.index, df['RSI'], label='RSI(14)')
    ax1.axhline(70, color='green', linestyle='--', label='Overbought (70)')
    ax1.axhline(30, color='red',   linestyle='--', label='Oversold (30)')
    ax1.set_ylabel('RSI')
    ax1.legend(loc='upper left')
    ax1.grid(True)

    # --- Bottom panel: MACD & Signal line ---
    ax2.plot(df.index, df['MACD'],        label='MACD (12–26)')
    ax2.plot(df.index, df['MACD_signal'], label='Signal (9-EMA)', lw=1)
    ax2.set_ylabel('MACD')
    ax2.legend(loc='upper left')
    ax2.grid(True)

    # Final formatting
    ax2.set_xlabel('Date')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
