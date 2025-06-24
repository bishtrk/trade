#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

def load_data(path):
    """Load scrip.csv, parse dates, strip commas, and rename OHLC columns."""
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'High Price': 'High',
        'Low Price':  'Low'
    }, inplace=True)
    return df

def detect_resistance_zone(df, swing_window, lookback):
    """
    1. Swing highs: mark bars whose High is a local maximum over ±swing_window bars.
    2. Resistance zone: rolling max of High over previous `lookback` bars.
    """
    df = df.copy()
    # Swing highs (local maxima)
    highs = df['High'].values
    idx = argrelextrema(highs, np.greater_equal, order=swing_window)[0]
    df['Swing_High'] = np.nan
    df.iloc[idx, df.columns.get_loc('Swing_High')] = df['High'].iloc[idx]

    # Resistance zone = shifted rolling max of High
    df['Resistance_Zone'] = (
        df['High']
          .shift(1)
          .rolling(window=lookback, min_periods=1)
          .max()
    )
    return df

def detect_consolidation_zone(df, cons_window, percentile):
    """
    1. Compute daily range (High - Low) and its rolling average over `cons_window` bars.
    2. Flag consolidation when that rolling average is below the Xth percentile of all such values.
    """
    df = df.copy()
    df['Range']     = df['High'] - df['Low']
    df['Avg_Range'] = df['Range'].rolling(window=cons_window, min_periods=1).mean()
    threshold = df['Avg_Range'].quantile(percentile)
    df['Consolidation_Zone'] = df['Avg_Range'] < threshold
    return df

def main():
    parser = argparse.ArgumentParser(description="Detect resistance and consolidation zones in TCS data")
    parser.add_argument('--csv',                 default='scrip.csv',
                        help="Path to your scrip.csv file")
    parser.add_argument('--swing-window',  type=int, default=5,
                        help="Bars on each side for local maxima (swing highs)")
    parser.add_argument('--resistance-lookback', type=int, default=20,
                        help="Days for rolling max resistance zone")
    parser.add_argument('--cons-window',    type=int, default=10,
                        help="Bars for rolling average range (consolidation)")
    parser.add_argument('--percentile',     type=float, default=0.3,
                        help="Percentile (0–1) threshold to flag consolidation")
    args = parser.parse_args()

    # Load and detect
    df = load_data(args.csv)
    df = detect_resistance_zone(df, args.swing_window, args.resistance_lookback)
    df = detect_consolidation_zone(df, args.cons_window, args.percentile)

    # Output Swing Highs (Resistance Points)
    swings = df['Swing_High'].dropna()
    if swings.empty:
        print("No swing highs detected.")
    else:
        print("\nSwing Highs (candidate resistance points):")
        print(swings.to_string(formatter='{:,.2f}'.format))

    # Show the latest Resistance Zone
    latest = df.index[-1]
    res_zone = df.at[latest, 'Resistance_Zone']
    print(f"\nResistance Zone (rolling max over last {args.resistance_lookback} days) at {latest.date()}: ₹{res_zone:,.2f}")

    # Output Consolidation Bars
    cons_days = df.index[df['Consolidation_Zone']]
    if cons_days.empty:
        print("\nNo consolidation periods detected.")
    else:
        print(f"\nConsolidation flagged on {len(cons_days)} bars (Avg Range < {args.percentile*100:.0f}th percentile):")
        for d in cons_days:
            print(" ", d.date())

if __name__ == '__main__':
    main()


#python detect_zones.py --csv scrip.csv \  --swing-window 5 \  --resistance-lookback 20 \  --cons-window 10 \  --percentile 0.3