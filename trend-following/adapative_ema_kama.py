import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt

# 1) Load & preprocess CSV
df = pd.read_csv('scrip.csv', dtype=str)
df['Date  '] = pd.to_datetime(df['Date  '].str.strip(), format='%d-%b-%Y')
df.set_index('Date  ', inplace=True)

for col in [
    'Open Price  ', 'High Price  ', 'Low Price  ',
    'Close Price  ', 'Total Traded Quantity  '
]:
    df[col] = df[col].str.replace(',', '').astype(float)


# 2) Strategy: Fast EMA vs. Kaufman’s AMA (KAMA)
class AdaptiveEMACrossover(bt.Strategy):
    params = dict(
        ema_period    = 20,  # Fast EMA period
        er_period     = 10,  # Efficiency Ratio look-back
        kama_fast_len = 2,   # KAMA “fast” smoothing constant
        kama_slow_len = 30   # KAMA “slow” smoothing constant
    )

    def __init__(self):
        # Fast EMA
        self.ema = bt.indicators.EMA(self.data.close,
                                     period=self.p.ema_period)

        # KAMA (correct args: fast & slow)
        self.kama = bt.indicators.KAMA(self.data.close,
                                       period=self.p.er_period,
                                       fast=self.p.kama_fast_len,
                                       slow=self.p.kama_slow_len)

        # Crossover signal
        self.cross = bt.indicators.CrossOver(self.ema, self.kama)

        self._current = {}
        self.trades   = []

    def next(self):
        if not self.position and self.cross[0] == 1:
            self.buy()
        elif self.position and self.cross[0] == -1:
            self.close()

    def notify_order(self, order):
        if order.status != order.Completed:
            return

        dt    = bt.num2date(order.executed.dt).date()
        price = order.executed.price

        if order.isbuy():
            self._current = {'entry_date': dt, 'entry_price': price}
        elif order.issell():
            self._current.update({
                'exit_date':  dt,
                'exit_price': price,
                'profit':     price - self._current['entry_price'],
                'profit_pct': (price - self._current['entry_price'])
                              / self._current['entry_price'] * 100
            })
            self.trades.append(self._current)
            self._current = {}


# 3) Backtest
cerebro = bt.Cerebro()
cerebro.addstrategy(AdaptiveEMACrossover)

datafeed = bt.feeds.PandasData(
    dataname=df,
    open='Open Price  ',
    high='High Price  ',
    low='Low Price  ',
    close='Close Price  ',
    volume='Total Traded Quantity  '
)
cerebro.adddata(datafeed)
cerebro.broker.setcash(100000)

strat = cerebro.run()[0]


# 4) Build & print trades + summary
trades_df = pd.DataFrame(strat.trades)
trades_df['hold_days'] = trades_df.apply(
    lambda r: (r['exit_date'] - r['entry_date']).days, axis=1
)

print("\n=== Executed Trades ===")
print(trades_df.to_string(index=False))

print("\n=== Summary ===")
tot = len(trades_df)
print(f" Total trades      : {tot}")
print(f" Total PnL         : {trades_df['profit'].sum():.2f}")
print(f" Win rate          : {(trades_df['profit']>0).mean()*100:.1f}%")
print(f" Avg PnL/trade     : {trades_df['profit'].mean():.2f}")
print(f" Avg hold duration : {trades_df['hold_days'].mean():.0f} days")


# 5) Plot price, EMA, KAMA & buy/sell markers
plt.figure(figsize=(14,6))
plt.plot(df.index, df['Close Price  '], label='Close Price')
plt.plot(df.index, strat.ema.array, label=f'EMA({strat.p.ema_period})')
plt.plot(df.index, strat.kama.array,
         label=f'KAMA(er={strat.p.er_period},fast={strat.p.kama_fast_len},slow={strat.p.kama_slow_len})')

for _, t in trades_df.iterrows():
    plt.scatter(t['entry_date'], t['entry_price'], marker='^', color='green')
    plt.scatter(t['exit_date'],  t['exit_price'],  marker='v', color='red')

plt.title("Adaptive EMA Crossover – Price with Buy/Sell Signals")
plt.legend()
plt.tight_layout()
plt.show()
