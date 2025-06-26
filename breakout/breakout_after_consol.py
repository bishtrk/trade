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
        'High Price':  'High',
        'Low Price':   'Low',
        'Close Price': 'Close',
        'Total Traded Quantity': 'Volume'  # if you have Volume in CSV
    }, inplace=True)
    return df

def detect_resistance_breakouts(df, lookback):
    df['Resistance'] = df['High'].shift(1) \
                         .rolling(window=lookback, min_periods=1).max()
    df['Price_Breakout'] = df['Close'] > df['Resistance']
    return df

def detect_consolidation(df, cons_window, long_window, percentile):
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

def plot_after_consol(df):
    # final signal
    df['Breakout_Consol'] = df['Price_Breakout'] & df['Consolidating']
    bo = df[df['Breakout_Consol']]

    fig, ax_price = plt.subplots(figsize=(12,6))

    # --- Price & Resistance ---
    ax_price.plot(df.index, df['Close'], label='Close', linewidth=1.2)
    ax_price.plot(df.index, df['Resistance'],
                  label='Resistance', linestyle='--', color='orange')

    # --- Consolidation shading ---
    ax_price.fill_between(df.index,
                          df['Low'], df['High'],
                          where=df['Consolidating'],
                          color='grey', alpha=0.3,
                          label='Consolidation')

    # --- Breakout markers ---
    ax_price.scatter(bo.index, bo['Close'],
                     marker='^', s=100, color='green',
                     label='Breakout after Consol', zorder=5)

    ax_price.set_ylabel('Price')
    ax_price.legend(loc='upper left')

    # --- Volume bars on twin axis ---
    ax_vol = ax_price.twinx()
    # all volume, light alpha
    ax_vol.bar(df.index, df['Volume'], width=1, align='center', alpha=0.3)
    # highlight the breakout-after-consol volumes
    ax_vol.bar(bo.index, bo['Volume'], width=1, align='center')
    ax_vol.set_ylabel('Volume')

    ax_price.set_title('Price, Volume & Breakouts After Consolidation')
    ax_price.set_xlabel('Date')
    plt.tight_layout()
    plt.show()


def main():
    p = argparse.ArgumentParser(description="Breakout after consolidation + volume plot")
    p.add_argument('--csv',            default='scrip.csv', help="Path to CSV")
    p.add_argument('--price-lookback', type=int, default=20, help="Resistance lookback days")
    p.add_argument('--cons-window',    type=int, default=10, help="Consolidation window")
    p.add_argument('--long-window',    type=int, default=50, help="Long window for threshold")
    p.add_argument('--percentile',     type=float, default=0.3, help="Percentile for squeeze")
    args = p.parse_args()

    df = load_data(args.csv)
    df = detect_resistance_breakouts(df, args.price_lookback)
    df = detect_consolidation(df, args.cons_window, args.long_window, args.percentile)

    # print signals
    bo = df[df['Price_Breakout'] & df['Consolidating']]
    if bo.empty:
        print("No breakouts after consolidation detected.")
    else:
        pd.set_option('display.float_format', '{:.2f}'.format)
        print("\nBreakouts After Consolidation:\n")
        print(bo[['Close','Resistance','Avg_Range','Cons_Threshold']])

    # and plot everything
    plot_after_consol(df)

if __name__ == '__main__':
    main()


#python breakout_after_consol.py --price-lookback 20 --cons-window 10 --long-window 50 --percentile 0.3
