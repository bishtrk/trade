#!/usr/bin/env python3
import argparse
import pandas as pd

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
    # Prior resistance = max High over last price_lookback days (shifted)
    df['Resistance'] = (
        df['High']
          .shift(1)
          .rolling(window=price_lookback, min_periods=1)
          .max()
    )
    # Price breakout if Close > that resistance
    df['Price_Breakout'] = df['Close'] > df['Resistance']
    return df

def apply_volume_filter(df, vol_lookback, vol_multiplier):
    # Lagged average volume
    df['Avg_Volume'] = (
        df['Volume']
          .shift(1)
          .rolling(window=vol_lookback, min_periods=1)
          .mean()
    )
    # Volume confirmation: today's volume > multiplier × average
    df['Volume_Confirm'] = df['Volume'] > vol_multiplier * df['Avg_Volume']
    # Only keep breakouts that also have volume confirmation
    df['Breakout_Valid'] = df['Price_Breakout'] & df['Volume_Confirm']
    return df

def main():
    p = argparse.ArgumentParser(description="Detect resistance breakouts with volume confirmation")
    p.add_argument('--csv',            default='scrip.csv',     help="Path to scrip.csv")
    p.add_argument('--lookback',       type=int, default=20,   help="Days to define resistance (price lookback)")
    p.add_argument('--vol-lookback',   type=int, default=20,   help="Days to compute average volume")
    p.add_argument('--vol-multiplier', type=float, default=1.5, help="Volume multiple for confirmation")
    args = p.parse_args()

    df = load_data(args.csv)
    df = detect_breakouts(df, args.lookback)
    df = apply_volume_filter(df, args.vol_lookback, args.vol_multiplier)

    valid = df[df['Breakout_Valid']]
    if valid.empty:
        print("No valid breakouts with volume confirmation.")
        return

    # Display the valid breakout days
    print(f"Breakouts (lookback={args.lookback}d) with Vol > {args.vol_multiplier}×{args.vol_lookback}d Avg:\n")
    print(valid[['Close','Resistance','Volume','Avg_Volume']].to_string(
        formatters={
            'Close':      '{:,.2f}'.format,
            'Resistance': '{:,.2f}'.format,
            'Volume':     '{:,.0f}'.format,
            'Avg_Volume': '{:,.0f}'.format
        }
    ))

if __name__ == '__main__':
    main()

#python breakout_with_volume.py --lookback 20 --vol-lookback 20 --vol-multiplier 1.5
    
# This code detects breakouts above prior resistance levels in stock data, with volume confirmation.
# It loads data from a CSV file, computes resistance levels based on historical highs,
# and checks for breakouts where the closing price exceeds this resistance.
# It also applies a volume filter to ensure that the breakout is supported by significant trading volume.