#can work with a mix of both EMA and SMA

#Backtrader is totally agnostic about which moving-average you pick. You can, for example, use a fast EMA against a slow SMA simply by swapping one indicator class
# inside your Strategy.__init__():
#self.ema_fast = bt.ind.EMA(self.data.close, period=self.p.pfast)
#self.sma_slow = bt.ind.SMA(self.data.close, period=self.p.pslow)
# and then
#self.crossover = bt.ind.CrossOver(self.ema_fast, self.sma_slow)

#From there your next() logic stays identical: buy when crossover>0, sell when <0. You can even parametrize both types in Strategy.params so you can backtest any mix of EMA/SMA without touching the core loop.

#!/usr/bin/env python3
import backtrader as bt
import pandas as pd

class SmaCross(bt.Strategy):
    params = dict(
        pfast=20,   # fast SMA period
        pslow=50    # slow SMA period
    )

    def __init__(self):
        sma_fast = bt.ind.SMA(self.data.close, period=self.p.pfast)
        sma_slow = bt.ind.SMA(self.data.close, period=self.p.pslow)
        # crossover signal: +1 when fast crosses above slow, -1 when below
        self.crossover = bt.ind.CrossOver(sma_fast, sma_slow)

    def next(self):
        # if not in the market, look for a bullish crossover
        if not self.position and self.crossover > 0:
            self.buy()
        # if in the market, look for a bearish crossover to exit
        elif self.position and self.crossover < 0:
            self.sell()

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # 1) Add the strategy
    cerebro.addstrategy(SmaCross)

    # 2) Load data from CSV via pandas
    df = pd.read_csv('scrip.csv', thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    # rename to what Backtrader expects
    df.rename(columns={
        'Open Price': 'Open',
        'High Price': 'High',
        'Low Price': 'Low',
        'Close Price': 'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)

    datafeed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(datafeed)

    # 3) Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # 4) Use full equity on each trade
    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)

    # 5) (Optional) No commission; set if you want realistic costs
    cerebro.broker.setcommission(commission=0.0)

    # 6) Print out the starting conditions
    print(f"Starting Portfolio Value: ₹{cerebro.broker.getvalue():.2f}")

    # 7) Run it
    strat = cerebro.run()[0]

    # 8) Print out the final result
    print(f"Final Portfolio Value:   ₹{cerebro.broker.getvalue():.2f}")

    # 9) Plot buy/sell arrows and equity below
    cerebro.plot(style='candlestick')
