# It adds an RSI‐based filter so that you only enter long when:
#20/50 SMA crossover and RSI is below an overbought threshold (default 70)
#Exit on the SMA cross back down and RSI is above an oversold threshold (default 30)

#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def load_data(path):
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={'Close Price':'Close'}, inplace=True)
    return df

def compute_indicators(df, fast, slow, rsi_period):
    # SMAs
    df['SMA_fast'] = df['Close'].rolling(window=fast, min_periods=1).mean()
    df['SMA_slow'] = df['Close'].rolling(window=slow, min_periods=1).mean()
    # RSI
    delta = df['Close'].diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=rsi_period, min_periods=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period, min_periods=rsi_period).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def generate_signals(df, rsi_oversold, rsi_overbought):
    # crossovers
    cross_up   = (df['SMA_fast'] > df['SMA_slow'])  & (df['SMA_fast'].shift(1) <= df['SMA_slow'].shift(1))
    cross_down = (df['SMA_fast'] < df['SMA_slow'])  & (df['SMA_fast'].shift(1) >= df['SMA_slow'].shift(1))
    # apply RSI filter
    long_signal  = cross_up   & (df['RSI'] < rsi_overbought)
    short_signal = cross_down & (df['RSI'] > rsi_oversold)
    df['long_signal']  = long_signal
    df['short_signal'] = short_signal
    return df

def backtest(df, initial_capital):
    cash = initial_capital
    position = 0.0
    trades = []
    equity = []

    for date, row in df.iterrows():
        price = row['Close']
        # buy
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
        # sell
        elif row['short_signal'] and position > 0:
            exit_price = price
            exit_date  = date
            cash       = position * price
            pnl        = position * (exit_price - trades[-1]['Entry Price'])
            ret        = (exit_price / trades[-1]['Entry Price'] - 1) * 100
            trades[-1].update({
                'Exit Date':   exit_date,
                'Exit Price':  exit_price,
                'PnL':         pnl,
                'Return (%)':  ret
            })
            position = 0.0

        equity.append(cash + position * price)

    equity_df = pd.DataFrame({'Equity': equity}, index=df.index)
    trades_df = pd.DataFrame(trades, columns=[
        'Entry Date','Entry Price','Exit Date','Exit Price','PnL','Return (%)'
    ])
    return equity_df, trades_df

def summarize_and_plot(equity_df, trades_df):
    total_init = len(trades_df)
    closed     = trades_df['Exit Date'].notna()
    wins       = (trades_df.loc[closed,'PnL'] > 0).sum()
    losses     = (trades_df.loc[closed,'PnL'] <= 0).sum()
    total_pnl  = trades_df.loc[closed,'PnL'].sum()

    print(f"\nTrades Initiated: {total_init}")
    print(f"Trades Closed:    {closed.sum()}")
    print(f"Wins: {wins}, Losses: {losses}")
    print(f"Overall Closed PnL: ₹{total_pnl:,.2f}\n")

    if total_init:
        print("=== Trade Log ===")
        print(trades_df.to_string(index=False))
    else:
        print("No trades were initiated.")

    plt.figure(figsize=(12,6))
    plt.plot(equity_df.index, equity_df['Equity'], label='Equity Curve')
    plt.title('Equity Curve – SMA+RSI Filter')
    plt.ylabel('Portfolio Value (₹)')
    plt.xlabel('Date')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--path',           default='scrip.csv')
    p.add_argument('--fast',  type=int, default=20)
    p.add_argument('--slow',  type=int, default=50)
    p.add_argument('--rsi-period',      type=int, default=14)
    p.add_argument('--rsi-oversold',    type=float, default=30.0)
    p.add_argument('--rsi-overbought',  type=float, default=70.0)
    p.add_argument('--capital',         type=float, default=100_000)
    args = p.parse_args()

    df = load_data(args.path)
    df = compute_indicators(df, args.fast, args.slow, args.rsi_period)
    df = generate_signals(df, args.rsi_oversold, args.rsi_overbought)
    equity_df, trades_df = backtest(df, args.capital)
    summarize_and_plot(equity_df, trades_df)

if __name__ == '__main__':
    import argparse
    main()
#python backtest_sma_rsi_filter.py --fast 20 --slow 50 --rsi-period 14 --rsi-oversold 30 --rsi-overbought 70