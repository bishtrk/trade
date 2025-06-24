#!/usr/bin/env python3
import argparse
import pandas as pd

def load_data(path):
    """
    Load scrip.csv, parse dates, strip commas, and rename OHLCV columns.
    """
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'Close Price': 'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)
    return df

def compute_macd(df, fast=12, slow=26, signal=9):
    """
    Compute MACD line and signal line.
    """
    exp1 = df['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    sig  = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig

def find_bullish_crossovers(macd, sig):
    """
    Identify bullish MACD crossovers: MACD crossing above its signal line.
    """
    prev_macd = macd.shift(1)
    prev_sig  = sig.shift(1)
    return (prev_macd < prev_sig) & (macd > sig)

def main():
    parser = argparse.ArgumentParser(description="MACD Crossovers with Volume Spike Filter")
    parser.add_argument('--csv',         default='scrip.csv', help="Path to scrip.csv")
    parser.add_argument('--vol-window',  type=int, default=20,   help="Window for average volume")
    parser.add_argument('--vol-mult',    type=float, default=1.5, help="Volume multiplier for spike")
    args = parser.parse_args()

    # Load data
    df = load_data(args.csv)

    # Compute MACD and signal line
    df['MACD'], df['MACD_SIG'] = compute_macd(df)

    # Identify bullish MACD crossovers
    df['Bullish_XO'] = find_bullish_crossovers(df['MACD'], df['MACD_SIG'])

    # Compute lagged average volume
    df['Avg_Volume'] = df['Volume'].shift(1).rolling(window=args.vol_window, min_periods=1).mean()

    # Volume spike filter
    df['Vol_Spike'] = df['Volume'] > args.vol_mult * df['Avg_Volume']

    # Final signal: both crossover and volume spike
    df['Signal'] = df['Bullish_XO'] & df['Vol_Spike']

    # Display results
    signals = df[df['Signal']]
    if signals.empty:
        print("No bullish MACD crossovers with volume spikes found.")
    else:
        print(f"Dates with MACD crossovers and volume > {args.vol_mult}×{args.vol_window}-day avg:\n")
        print(signals[['Close','Volume','Avg_Volume','MACD','MACD_SIG']].to_string(
            header=['Close','Vol','AvgVol','MACD','Signal'],
            float_format='{:,.2f}'.format
        ))

if __name__ == '__main__':
    main()

#python macd_volume_spike.py --vol-window 20 --vol-mult 1.5
# This script runs the MACD volume spike strategy with specified parameters.
# The `--vol-window` parameter sets the window size for volume calculation,