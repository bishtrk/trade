#!/usr/bin/env python3
"""
MACD Crossover Backtest with Price, Volume, and MACD Plot

Usage:
    python backtest_macd_price_volume.py

Requires:
    pip install pandas matplotlib
"""
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # 1. Load data
    df = pd.read_csv('scrip.csv', thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'Close Price': 'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)

    # 2. MACD parameters
    fast_period   = 12
    slow_period   = 26
    signal_period = 9
    initial_capital = 100_000

    # 3. Compute EMAs and MACD
    df['EMA_fast']    = df['Close'].ewm(span=fast_period,   adjust=False).mean()
    df['EMA_slow']    = df['Close'].ewm(span=slow_period,   adjust=False).mean()
    df['MACD']        = df['EMA_fast'] - df['EMA_slow']
    df['MACD_signal'] = df['MACD'].ewm(span=signal_period, adjust=False).mean()

    # 4. Generate crossover signals
    df['long_signal']  = (df['MACD'] > df['MACD_signal']) & (df['MACD'].shift(1) <= df['MACD_signal'].shift(1))
    df['short_signal'] = (df['MACD'] < df['MACD_signal']) & (df['MACD'].shift(1) >= df['MACD_signal'].shift(1))

    # 5. Backtest loop
    cash = initial_capital
    position = 0.0
    trades = []
    equity_curve = []

    for date, row in df.iterrows():
        price = row['Close']

        # Entry
        if row['long_signal'] and position == 0:
            entry_price = price
            entry_date  = date
            position    = cash / price
            cash        = 0.0
            trades.append({
                'Entry Date':  entry_date,
                'Entry Price': entry_price,
                'Exit Date':   pd.NaT,
                'Exit Price':  None,
                'PnL':         None,
                'Return (%)':  None
            })

        # Exit
        elif row['short_signal'] and position > 0:
            exit_price = price
            exit_date  = date
            pnl  = position * (exit_price - trades[-1]['Entry Price'])
            ret  = (exit_price / trades[-1]['Entry Price'] - 1) * 100
            trades[-1].update({
                'Exit Date':   exit_date,
                'Exit Price':  exit_price,
                'PnL':         pnl,
                'Return (%)':  ret
            })
            cash     = position * price
            position = 0.0

        # Equity update
        equity_curve.append(cash + position * price)

    # 6. Summarize
    trades_df = pd.DataFrame(trades)
    equity_df = pd.DataFrame({'Equity': equity_curve}, index=df.index)

    total   = len(trades_df)
    closed  = trades_df['Exit Date'].notna().sum()
    wins    = (trades_df['PnL'] > 0).sum()
    losses  = (trades_df['PnL'] <= 0).sum()
    overall = trades_df['PnL'].sum() if closed > 0 else 0.0

    print(f"Total Trades Initiated: {total}")
    print(f"Total Trades Closed:    {closed}")
    print(f"Wins: {wins}, Losses: {losses}")
    print(f"Overall Closed PnL: ₹{overall:,.2f}\n")

    if total > 0:
        print("=== Trade Log ===")
        print(trades_df.to_string(index=False))

    # 7. Plot combined chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Top: Price + Volume
    ax1.plot(df.index, df['Close'], label='Close Price')
    ax1.set_ylabel('Price (₹)')
    ax1.legend(loc='upper left')
    ax1b = ax1.twinx()
    ax1b.bar(df.index, df['Volume'], width=1.0, alpha=0.3, label='Volume', color='gray')
    ax1b.set_ylabel('Volume')
    ax1b.legend(loc='upper right')

    # Bottom: MACD & Signal
    ax2.plot(df.index, df['MACD'],        label='MACD Line')
    ax2.plot(df.index, df['MACD_signal'], label='Signal Line', linestyle='--')
    ax2.axhline(0, color='black', linewidth=0.7)
    ax2.set_title('MACD & Signal Line')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('MACD')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
