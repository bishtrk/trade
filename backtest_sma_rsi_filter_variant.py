Milestone: Dual-Filter Entry
Design a rule that only buys when:

Primary Trigger: 20/50 SMA crossover (fast SMA crosses above slow SMA).

Secondary Filter: RSI (14-period) is below 30 (i.e., price is “oversold” despite the crossover).

Rationale: You wait for a trend shift (SMA crossover) but only enter when momentum has pulled back enough (RSI <30) to optimize your entry price and avoid diving in at an extreme.

Backtest: Compare trade frequency, win rate, and drawdown against the pure SMA-only strategy to see how much noise you’ve eliminated and whether your returns improved.

By layering oscillators, volume, and volatility filters—then insisting on confluence—you’ll craft signals that are both timely and robust.

What it does
Loads scrip.csv and parses dates.
Computes 20/50 SMAs and 14-day RSI.
Generates a long signal only when the SMA crossover occurs and RSI < 30; exits on the SMA cross back.
Runs a loop to simulate entries/exits, recording each trade, its PnL, and building an equity curve.
Prints a trade summary and displays the equity curve chart.


#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # 1. Load your data
    df = pd.read_csv('scrip.csv', thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={'Close Price': 'Close'}, inplace=True)

    # 2. Parameters
    fast, slow = 20, 50          # SMA windows
    rsi_period = 14              # RSI look-back
    rsi_threshold = 30           # only buy when RSI < this
    initial_capital = 100000     # starting cash

    # 3. Compute SMAs
    df['SMA_fast'] = df['Close'].rolling(window=fast, min_periods=1).mean()
    df['SMA_slow'] = df['Close'].rolling(window=slow, min_periods=1).mean()

    # 4. Compute RSI
    delta = df['Close'].diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=rsi_period, min_periods=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period, min_periods=rsi_period).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 5. Generate dual-filter signals
    df['long_signal'] = (
        (df['SMA_fast'] > df['SMA_slow']) &
        (df['SMA_fast'].shift(1) <= df['SMA_slow'].shift(1)) &
        (df['RSI'] < rsi_threshold)
    )
    df['short_signal'] = (
        (df['SMA_fast'] < df['SMA_slow']) &
        (df['SMA_fast'].shift(1) >= df['SMA_slow'].shift(1))
    )

    # 6. Backtest loop
    cash = initial_capital
    position = 0
    trades = []
    equity_curve = []

    for date, row in df.iterrows():
        price = row['Close']

        # entry
        if row['long_signal'] and position == 0:
            entry_date, entry_price = date, price
            position = cash / price
            cash = 0
            trades.append({
                'Entry Date':   entry_date,
                'Entry Price':  entry_price,
                'Exit Date':    pd.NaT,
                'Exit Price':   None,
                'PnL':          None,
                'Return (%)':   None
            })

        # exit
        elif row['short_signal'] and position > 0:
            exit_date, exit_price = date, price
            pnl    = position * (exit_price - trades[-1]['Entry Price'])
            ret    = (exit_price / trades[-1]['Entry Price'] - 1) * 100
            trades[-1].update({
                'Exit Date':   exit_date,
                'Exit Price':  exit_price,
                'PnL':         pnl,
                'Return (%)':  ret
            })
            cash = position * price
            position = 0

        # equity update
        equity_curve.append(cash + position * price)

    # 7. Results & summary
    trades_df = pd.DataFrame(trades)
    equity_df = pd.DataFrame({'Equity': equity_curve}, index=df.index)

    total   = len(trades_df)
    closed  = trades_df['Exit Date'].notna().sum()
    wins    = (trades_df['PnL'] > 0).sum()
    losses  = (trades_df['PnL'] <= 0).sum()
    overall = trades_df['PnL'].sum() if closed > 0 else 0

    print(f"Total Trades Initiated: {total}")
    print(f"Total Trades Closed:    {closed}")
    print(f"Wins: {wins}, Losses: {losses}")
    print(f"Overall Closed PnL: ₹{overall:,.2f}\n")

    if total > 0:
        print("=== Trade Log ===")
        print(trades_df.to_string(index=False))

    # 8. Plot equity curve
    plt.figure(figsize=(12,6))
    plt.plot(equity_df.index, equity_df['Equity'], label='Equity Curve')
    plt.title('Equity Curve – SMA20/50 + RSI Filter')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value (₹)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
