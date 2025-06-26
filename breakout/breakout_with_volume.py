#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def load_data(path):
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'High Price':            'High',
        'Close Price':           'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)
    return df

def detect_breakouts(df, price_lookback):
    df['Resistance'] = (
        df['High']
          .shift(1)
          .rolling(window=price_lookback, min_periods=1)
          .max()
    )
    df['Price_Breakout'] = df['Close'] > df['Resistance']
    return df

def apply_volume_filter(df, vol_lookback, vol_multiplier):
    df['Avg_Volume'] = (
        df['Volume']
          .shift(1)
          .rolling(window=vol_lookback, min_periods=1)
          .mean()
    )
    df['Volume_Confirm'] = df['Volume'] > vol_multiplier * df['Avg_Volume']
    df['Breakout_Valid'] = df['Price_Breakout'] & df['Volume_Confirm']
    return df

def plot_breakouts(df, valid):
    # Single chart with price + volume on twin y-axes
    fig, ax_price = plt.subplots(figsize=(12, 6))

    # Price lines and breakout markers
    ax_price.plot(df.index, df['Close'], label='Close')
    ax_price.plot(df.index, df['Resistance'], label='Resistance')
    ax_price.scatter(valid.index, valid['Close'], marker='o', label='Valid Breakout', zorder=5)
    ax_price.set_ylabel('Price')
    ax_price.legend(loc='upper left')

    # Volume bars on a second y-axis
    ax_vol = ax_price.twinx()
    # all volume bars (first default color)
    ax_vol.bar(df.index, df['Volume'], width=1, align='center')
    # highlight valid breakout volumes (next default color)
    ax_vol.bar(valid.index, valid['Volume'], width=1, align='center')
    ax_vol.set_ylabel('Volume')

    ax_price.set_title('Price & Volume – Breakouts Highlighted')
    ax_price.set_xlabel('Date')
    plt.tight_layout()
    plt.show()

def main():
    p = argparse.ArgumentParser(description="Detect and plot breakouts with volume confirmation")
    p.add_argument('--csv',            default='scrip.csv',     help="Path to CSV file")
    p.add_argument('--lookback',       type=int, default=20,    help="Price lookback days")
    p.add_argument('--vol-lookback',   type=int, default=20,    help="Volume lookback days")
    p.add_argument('--vol-multiplier', type=float, default=1.5,  help="Volume multiplier")
    args = p.parse_args()

    df = load_data(args.csv)
    df = detect_breakouts(df, args.lookback)
    df = apply_volume_filter(df, args.vol_lookback, args.vol_multiplier)

    valid = df[df['Breakout_Valid']]
    if valid.empty:
        print("No valid breakouts with volume confirmation.")
        return

    # Console table only
    print(f"Breakouts (lookback={args.lookback}d) with Vol > {args.vol_multiplier}×{args.vol_lookback}d Avg:\n")
    print(valid[['Close','Resistance','Volume','Avg_Volume']].to_string(
        formatters={
            'Close':      '{:,.2f}'.format,
            'Resistance': '{:,.2f}'.format,
            'Volume':     '{:,.0f}'.format,
            'Avg_Volume': '{:,.0f}'.format
        }
    ))

    plot_breakouts(df, valid)

if __name__ == '__main__':
    main()
