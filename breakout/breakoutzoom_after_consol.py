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
        'Low Price':             'Low',
        'Close Price':           'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)
    for col in ['High','Low','Close','Volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def detect_zoom_breakout(df, cons_days, zoom_pct):
    df = df.copy()
    df['Max_Close'] = (
        df['Close']
          .rolling(window=cons_days, min_periods=cons_days)
          .max()
          .shift(1)
    )
    df['Pct_Above'] = df['Close'] / df['Max_Close'] - 1.0
    df['Zoom_Breakout'] = df['Pct_Above'] >= zoom_pct
    return df

def plot_zoom(df, zoom_dates, cons_days, zoom_pct):
    fig, ax1 = plt.subplots(figsize=(12,6))
    ax1.plot(df.index, df['Close'], label='Close', lw=1.2)
    ax1.scatter(zoom_dates, df.loc[zoom_dates,'Close'],
                marker='o', color='red', label='Zoom Breakout', zorder=5)
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.bar(df.index, df['Volume'], width=1, alpha=0.3)
    ax2.set_ylabel('Volume')

    plt.title(f'Zoom ≥{zoom_pct*100:.1f}% after {cons_days}-day coil')
    plt.tight_layout()
    plt.show()

def main():
    p = argparse.ArgumentParser(description="Simple coil→zoom screener")
    p.add_argument('--csv',       default='scrip.csv', help="Path to CSV file")
    p.add_argument('--cons-days', type=int,   default=30,  help="Consolidation window (days)")
    p.add_argument('--zoom-pct',  type=float, default=0.02, help="Zoom threshold (e.g. 0.10=10%)")
    args = p.parse_args()

    df = load_data(args.csv)
    df = detect_zoom_breakout(df, args.cons_days, args.zoom_pct)
    zoomed = df[df['Zoom_Breakout']]

    if zoomed.empty:
        print("No zoom breakouts detected.")
    else:
        # Print raw numbers with two decimals (Pct_Above with four decimals)
        print(zoomed[['Close','Max_Close','Pct_Above']].to_string(
            formatters={
                'Close':     '{:,.2f}'.format,
                'Max_Close': '{:,.2f}'.format,
                'Pct_Above': '{:.4f}'.format,
            }
        ))
        plot_zoom(df, zoomed.index, args.cons_days, args.zoom_pct)

if __name__ == '__main__':
    main()
