#!/usr/bin/env python3
import argparse
import pandas as pd

def load_data(path):
    """Load scrip.csv, parse dates, strip commas, rename OHLC columns."""
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={'Close Price':'Close'}, inplace=True)
    return df

def compute_macd(df, fast=12, slow=26, signal=9):
    """Compute MACD line and signal line."""
    exp1 = df['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    sig  = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig

def find_bullish_crossovers(macd, sig):
    """Return boolean Series where MACD crosses above Signal line."""
    prev_macd = macd.shift(1)
    prev_sig  = sig.shift(1)
    return (prev_macd < prev_sig) & (macd > sig)

def main():
    parser = argparse.ArgumentParser(description="MACD Histogram 'Punch' Filter")
    parser.add_argument('--csv',          default='scrip.csv', help="Path to scrip.csv")
    parser.add_argument('--hist-window',  type=int,   default=10,    help="Window for avg histogram height")
    parser.add_argument('--hist-mult',    type=float, default=0.5,   help="Multiplier of avg hist height for punch")
    args = parser.parse_args()

    # Load data
    df = load_data(args.csv)

    # Compute MACD & signal
    df['MACD'], df['MACD_SIG'] = compute_macd(df)

    # Compute histogram (distance between MACD and signal)
    df['HIST'] = df['MACD'] - df['MACD_SIG']

    # Identify bullish MACD crossovers
    df['Bullish_XO'] = find_bullish_crossovers(df['MACD'], df['MACD_SIG'])

    # Compute rolling average of absolute histogram height (lagged by 1)
    df['Avg_HIST'] = df['HIST'].abs().rolling(window=args.hist_window, min_periods=1).mean().shift(1)

    # Histogram Punch: require HIST > hist_mult * Avg_HIST on crossover day
    df['Punch_OK'] = df['Bullish_XO'] & (df['HIST'] > args.hist_mult * df['Avg_HIST'])

    # Show results
    signals = df[df['Punch_OK']]
    if signals.empty:
        print("No MACD crossovers with sufficient histogram punch found.")
    else:
        print("Dates where bullish MACD crossovers had >{:.0%} histogram punch:".format(args.hist_mult))
        print(signals[['Close','MACD','MACD_SIG','HIST','Avg_HIST']].to_string(
            header=['Close','MACD','Signal','Hist','AvgHist'],
            float_format='{:,.2f}'.format
        ))

if __name__ == '__main__':
    main()



#python macd_histogram_punch.py --hist-window 10 --hist-mult 0.5
