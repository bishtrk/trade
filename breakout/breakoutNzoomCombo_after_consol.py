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
    df = df[~df.index.duplicated(keep='first')]
    return df


def detect_consolidation(df, cons_window, long_window, percentile):
    df = df.copy()
    df['Range'] = df['High'] - df['Low']
    df['Avg_Range'] = (
        df['Range'].shift(1)
                  .rolling(window=cons_window, min_periods=1)
                  .mean()
    )
    df['Cons_Threshold'] = (
        df['Avg_Range']
          .rolling(window=long_window, min_periods=1)
          .quantile(percentile)
          .shift(1)
    )
    df['Consolidating'] = df['Avg_Range'] < df['Cons_Threshold']
    return df


def detect_zoom(df, cons_window, zoom_pct):
    df = df.copy()
    df['Max_Close'] = (
        df['Close']
          .rolling(window=cons_window, min_periods=cons_window)
          .max()
          .shift(1)
    )
    df['Pct_Above'] = df['Close'] / df['Max_Close'] - 1.0
    df['Zoom_Breakout'] = df['Pct_Above'] >= zoom_pct
    return df


def plot_signals(df, signals):
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(df.index, df['Close'], label='Close', lw=1)
    # shade consolidation
    ax.fill_between(df.index, df['Low'], df['High'], where=df['Consolidating'], color='grey', alpha=0.3, label='Consolidation')
    # mark zoom breakouts
    ax.scatter(signals.index, signals['Close'], marker='o', color='red', label='Zoom Signal', zorder=5)
    ax.set_ylabel('Price')
    ax.legend(loc='upper left')

    ax2 = ax.twinx()
    ax2.bar(df.index, df['Volume'], width=1, alpha=0.2)
    ax2.set_ylabel('Volume')

    plt.title(f"Zoom ≥{zoom_pct*100:.1f}% after {cons_window}-day coil")
    plt.tight_layout()
    plt.show()


def main():
    p = argparse.ArgumentParser(description="Combined low-volatility coil + zoom breakout signal")
    p.add_argument('--csv',         default='scrip.csv',  help='Path to CSV file')
    p.add_argument('--cons-window', type=int,   default=10,   help='Days of consolidation coil')
    p.add_argument('--long-window', type=int,   default=50,   help='History window for squeeze threshold')
    p.add_argument('--percentile',  type=float, default=0.3,  help='Percentile for low-volatility squeeze')
    p.add_argument('--zoom-pct',    type=float, default=0.1,  help='Min zoom % above coil high')
    args = p.parse_args()

    df = load_data(args.csv)
    df = detect_consolidation(df, args.cons_window, args.long_window, args.percentile)
    df = detect_zoom(df, args.cons_window, args.zoom_pct)
    # final signal: both conditions met
    df['Signal'] = df['Consolidating'] & df['Zoom_Breakout']
    signals = df[df['Signal']]

    if signals.empty:
        print("No combined coil+zoom signals detected.")
    else:
        # print table
        rows = []
        for dt, row in signals.iterrows():
            rows.append({
                'Date':         dt.strftime('%Y-%m-%d'),
                'Close':        row['Close'],
                'Max_Close':    row['Max_Close'],
                'Pct_Above':    row['Pct_Above'],
                'Avg_Range':    row['Avg_Range'],
                'Threshold':    row['Cons_Threshold'],
            })
        table = pd.DataFrame(rows).set_index('Date')
        print(table.to_string(
            float_format=lambda x: f"{x:.4f}" if abs(x)<1 else f"{x:,.2f}"
        ))
        plot_signals(df, signals)

if __name__ == '__main__':
    main()