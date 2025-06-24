#!/usr/bin/env python3
import backtrader as bt
import pandas as pd
from datetime import datetime

class SmaCross(bt.Strategy):
    params = dict(pfast=20, pslow=50)

    def __init__(self):
        # your two SMAs must live on self so they update each bar
        self.sma_fast  = bt.ind.SMA(self.data.close, period=self.p.pfast)
        self.sma_slow  = bt.ind.SMA(self.data.close, period=self.p.pslow)
        self.crossover = bt.ind.CrossOver(self.sma_fast, self.sma_slow)

        # prepare to record trades
        self.trades = []            # list of dicts
        self._entry = {}            # will hold entry details until we sell

    def next(self):
        if not self.position and self.crossover[0] > 0:
            # signal to buy
            self.buy()
        elif self.position and self.crossover[0] < 0:
            # signal to sell
            self.sell()

    def notify_order(self, order):
        if order.status != order.Completed:
            return

        dt    = bt.num2date(order.executed.dt).date()
        price = order.executed.price
        size  = order.executed.size

        if order.isbuy():
            # record entry
            self._entry = {
                'Entry Date':  dt,
                'Entry Price': price,
                'Size':        size
            }
            print(f"BUY EXECUTED on {dt} @ ₹{price:.2f}")
        else:
            # record exit and compute PnL
            entry = self._entry
            pnl  = (price - entry['Entry Price']) * entry['Size']
            ret  = (price / entry['Entry Price'] - 1) * 100

            self.trades.append({
                'Entry Date':   entry['Entry Date'],
                'Exit Date':    dt,
                'Entry Price':  entry['Entry Price'],
                'Exit Price':   price,
                'PnL':          pnl,
                'Return (%)':   ret
            })
            print(f"SELL EXECUTED on {dt} @ ₹{price:.2f}  PnL=₹{pnl:.2f}  Return={ret:.2f}%")

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross)

    # — Load & prep data —
    df = pd.read_csv('scrip.csv', thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)   # ascending dates
    df.rename(columns={
        'Open Price':            'Open',
        'High Price':            'High',
        'Low Price':             'Low',
        'Close Price':           'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)

    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    # — Broker & sizing —
    cerebro.broker.setcash(100_000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)  # one share per trade
    cerebro.broker.setcommission(commission=0.0)

    # — Run —
    print(f"Starting Portfolio Value: ₹{cerebro.broker.getvalue():.2f}")
    strat = cerebro.run()[0]
    print(f"Final Portfolio Value:   ₹{cerebro.broker.getvalue():.2f}\n")

    # — Build & print your trade-details table —
    trades_df = pd.DataFrame(strat.trades)
    if trades_df.empty:
        print("No trades were completed.")
    else:
        closed = trades_df['Exit Date'].notna()
        total  = len(trades_df)
        wins   = (trades_df.loc[closed, 'PnL'] > 0).sum()
        losses = (trades_df.loc[closed, 'PnL'] <= 0).sum()
        overall = trades_df.loc[closed, 'PnL'].sum()

        print(f"Total Trades Initiated: {total}")
        print(f"Total Trades Closed:    {closed.sum()}")
        print(f"Wins: {wins}, Losses: {losses}")
        print(f"Overall Closed PnL: ₹{overall:,.2f}\n")

        print("=== Trade Log ===")
        print(trades_df.to_string(index=False))

    # — Finally, plot your buy/sell arrows & equity curve —
    cerebro.plot(style='candlestick')
