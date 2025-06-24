#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

def load_data(path='scrip.csv'):
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={'Close Price':'Close'}, inplace=True)
    return df

def generate_signals(df, fast=20, slow=50):
    df['SMA_fast'] = df['Close'].rolling(window=fast, min_periods=1).mean()
    df['SMA_slow'] = df['Close'].rolling(window=slow, min_periods=1).mean()
    df['long_signal'] = (
        (df['SMA_fast'] > df['SMA_slow']) &
        (df['SMA_fast'].shift(1) <= df['SMA_slow'].shift(1))
    )
    df['short_signal'] = (
        (df['SMA_fast'] < df['SMA_slow']) &
        (df['SMA_fast'].shift(1) >= df['SMA_slow'].shift(1))
    )
    return df

def backtest_with_stats(df, initial_capital=100_000):
    cash = initial_capital
    position = 0.0
    trades = []       # list of dicts
    equity_curve = []

    for date, row in df.iterrows():
        price = row['Close']

        # BUY: record a new trade with blank exit
        if row['long_signal'] and position == 0:
            position = cash / price
            cash = 0.0
            trades.append({
                'Entry Date':   date,
                'Entry Price':  price,
                'Exit Date':    pd.NaT,
                'Exit Price':   None,
                'PnL':          None,
                'Return (%)':   None
            })

        # SELL: fill exit on the last open trade
        elif row['short_signal'] and position > 0:
            cash = position * price
            position = 0.0
            # fill in the last trade
            last = trades[-1]
            last['Exit Date']  = date
            last['Exit Price'] = price
            pnl = last['Entry Price'] and (last['Entry Price'], None)  # placeholder

            # compute PnL & %
            pnl  = (last['Exit Price'] - last['Entry Price']) * (cash / last['Exit Price'])
            ret  = (last['Exit Price'] / last['Entry Price'] - 1) * 100
            last['PnL']        = pnl
            last['Return (%)'] = ret

        # equity = cash + mark-to-market
        equity_curve.append(cash + position * price)

    equity_df  = pd.DataFrame({'Equity': equity_curve}, index=df.index)
    cols = ['Entry Date','Exit Date','Entry Price','Exit Price','PnL','Return (%)']
    trades_df  = pd.DataFrame(trades, columns=cols)
    return equity_df, trades_df

def summarize_and_plot(equity_df, trades_df):
    total_initiated = len(trades_df)
    closed = trades_df['Exit Date'].notna()
    total_closed    = closed.sum()
    wins            = (trades_df.loc[closed, 'PnL'] > 0).sum()
    losses          = (trades_df.loc[closed, 'PnL'] <= 0).sum()
    overall_pnl     = trades_df.loc[closed, 'PnL'].sum()

    print(f"\nTotal Trades Initiated: {total_initiated}")
    print(f"Total Trades Closed:    {total_closed}")
    print(f"Wins: {wins}, Losses: {losses}")
    print(f"Overall Closed PnL: ₹{overall_pnl:,.2f}\n")

    if total_initiated > 0:
        print("=== Trade Log ===")
        print(trades_df.to_string(index=False))
    else:
        print("No trades were initiated.")

    # Plot equity
    plt.figure(figsize=(12,6))
    plt.plot(equity_df.index, equity_df['Equity'], label='Equity Curve')
    plt.title('Equity Curve – SMA Crossover Strategy')
    plt.ylabel('Portfolio Value (₹)')
    plt.xlabel('Date')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    df = load_data()
    df = generate_signals(df, fast=50, slow=200)
    #    df = generate_signals(df, fast=10, slow=30) winning strategy for 1 year trent upto 24 jun 2025
    equity_df, trades_df = backtest_with_stats(df, initial_capital=100_000)
    summarize_and_plot(equity_df, trades_df)

if __name__ == "__main__":
    main()
