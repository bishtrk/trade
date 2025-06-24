#!/usr/bin/env python3
import pandas as pd

def load_data(path='scrip.csv'):
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    # we only need Close, High, Low, Open for MACD/SMA but ensure Close is present
    df.rename(columns={'Close Price':'Close'}, inplace=True)
    return df

def compute_sma(df, window=200):
    return df['Close'].rolling(window).mean()

def compute_macd(df, fast=12, slow=26, signal=9):
    exp1 = df['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    sig  = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig

def find_bullish_crossovers(macd, sig):
    prev_macd = macd.shift(1)
    prev_sig  = sig.shift(1)
    return (prev_macd < prev_sig) & (macd > sig)

def main():
    df = load_data()
    # 1. Compute SMA200 (for trend filter if you want)
    df['SMA200'] = compute_sma(df, 200)

    # 2. Compute MACD & signal
    df['MACD'], df['MACD_SIG'] = compute_macd(df)

    # 3. Identify bullish MACD crossovers
    df['Bullish_XO'] = find_bullish_crossovers(df['MACD'], df['MACD_SIG'])

    # 4. Zero-line confirmation: only keep crossovers where MACD > 0
    df['ZeroLine_OK'] = df['Bullish_XO'] & (df['MACD'] > 0)

    # 5. (Optional) Combine with trend filter: price above SMA200
    df['Trend_OK'] = df['Close'] > df['SMA200']
    df['Final_Signal'] = df['ZeroLine_OK'] & df['Trend_OK']

    # 6. Print results
    signals = df[df['ZeroLine_OK']]
    if signals.empty:
        print("No bullish MACD crossovers above zero line found.")
    else:
        print("\nBullish MACD crossovers ABOVE zero line:\n")
        print(signals[['Close','MACD','MACD_SIG']].to_string(
            header=['Close','MACD','Signal Line'],
            float_format='{:,.2f}'.format
        ))

    # If you want to enforce both trend+zero-line:
    both = df[df['Final_Signal']]
    if not both.empty:
        print("\n-- Of those, the following also had Close > SMA200 --\n")
        print(both[['Close','SMA200','MACD','MACD_SIG']].to_string(
            header=['Close','SMA200','MACD','Signal'],
            float_format='{:,.2f}'.format
        ))

if __name__ == '__main__':
    main()
