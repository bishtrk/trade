#!/usr/bin/env python3
import pandas as pd

def load_data(path='scrip.csv'):
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'Close Price':'Close'
    }, inplace=True)
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
    # True where MACD crosses above Signal
    prev_macd = macd.shift(1)
    prev_sig  = sig.shift(1)
    return (prev_macd < prev_sig) & (macd > sig)

def main():
    df = load_data()
    # 1. SMA200
    df['SMA200'] = compute_sma(df, 200)
    # 2. MACD + signal
    df['MACD'], df['MACD_SIG'] = compute_macd(df)
    # 3. Bullish crossovers
    df['Bullish_MACD_XO'] = find_bullish_crossovers(df['MACD'], df['MACD_SIG'])
    # 4. Trend filter: only keep those where price > SMA200
    df['MACD_Trend_Filter'] = df['Bullish_MACD_XO'] & (df['Close'] > df['SMA200'])

    # Print results
    signals = df[df['MACD_Trend_Filter']]
    if signals.empty:
        print("No bullish MACD crossovers above the 200-day SMA found.")
    else:
        print("Dates of bullish MACD crossovers while Close > SMA200:\n")
        print(signals[['Close','SMA200','MACD','MACD_SIG']].to_string(
            header=['Close','SMA200','MACD','Signal'],
            float_format='{:,.2f}'.format
        ))

if __name__ == '__main__':
    main()
