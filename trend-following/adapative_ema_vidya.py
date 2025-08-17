import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────────────────
# 1) LOAD & CLEAN YOUR DATA
# ──────────────────────────────────────────────────────────────────────────────
df = pd.read_csv('scrip.csv', dtype=str)
df['Date  '] = pd.to_datetime(df['Date  '].str.strip(), format='%d-%b-%Y')
df.set_index('Date  ', inplace=True)

for col in ['Open Price  ', 'High Price  ', 'Low Price  ',
            'Close Price  ', 'Total Traded Quantity  ']:
    df[col] = df[col].str.replace(',', '').astype(float)


# ──────────────────────────────────────────────────────────────────────────────
# 2) CUSTOM VIDYA INDICATOR
# ──────────────────────────────────────────────────────────────────────────────
class VIDYA(bt.Indicator):
    lines = ('vidya',)
    params = dict(period=20, vol_period=10)

    def __init__(self):
        self.vol   = bt.ind.StdDev(self.data, period=self.p.vol_period)
        self.avol  = bt.ind.SMA(self.vol, period=self.p.vol_period)
        self.kc    = 2.0 / (self.p.period + 1)
        self.addminperiod(self.p.vol_period)

    def next(self):
        if len(self) == 1:  # seed first value
            self.l.vidya[0] = self.data[0]
            return
        ratio = (self.vol[0] / self.avol[0]) if self.avol[0] else 0
        alpha = max(0.0, min(1.0, ratio * self.kc))
        self.l.vidya[0] = alpha * self.data[0] + (1 - alpha) * self.l.vidya[-1]


# ──────────────────────────────────────────────────────────────────────────────
# 3) STRATEGY: EMA vs VIDYA
# ──────────────────────────────────────────────────────────────────────────────
class VidyaStrategy(bt.Strategy):
    params = dict(ema_period=20, vidya_period=20, vol_period=10)

    def __init__(self):
        self.ema   = bt.ind.EMA(self.data.close, period=self.p.ema_period)
        self.vidya = VIDYA(self.data.close,
                           period=self.p.vidya_period,
                           vol_period=self.p.vol_period)
        self.cross = bt.ind.CrossOver(self.ema, self.vidya.vidya)
        self._cur   = {}
        self.trades = []

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
            self._cur = {'entry_date': dt, 'entry_price': price}
        elif order.issell():
            self._cur.update({
                'exit_date':  dt,
                'exit_price': price,
                'profit':     price - self._cur['entry_price'],
                'profit_pct': (price - self._cur['entry_price']) / self._cur['entry_price'] * 100
            })
            self.trades.append(self._cur)
            self._cur = {}


# ──────────────────────────────────────────────────────────────────────────────
# 4) RUN BACKTEST
# ──────────────────────────────────────────────────────────────────────────────
cerebro = bt.Cerebro()
cerebro.addstrategy(VidyaStrategy)

data = bt.feeds.PandasData(
    dataname=df,
    open='Open Price  ',
    high='High Price  ',
    low='Low Price  ',
    close='Close Price  ',
    volume='Total Traded Quantity  ',
)
cerebro.adddata(data)
cerebro.broker.setcash(100000)

strat = cerebro.run()[0]


# ──────────────────────────────────────────────────────────────────────────────
# 5) BUILD TRADES DATAFRAME & ADD hold_days
# ──────────────────────────────────────────────────────────────────────────────
# Convert the list of trade dicts into a DataFrame
trades_df = pd.DataFrame(strat.trades)

# If empty, predefine columns
expected_cols = ['entry_date','entry_price','exit_date','exit_price','profit','profit_pct']
if trades_df.empty:
    trades_df = pd.DataFrame(columns=expected_cols + ['hold_days'])
else:
    # Compute hold_days as integer difference
    trades_df['hold_days'] = trades_df.apply(
        lambda r: (r['exit_date'] - r['entry_date']).days, axis=1
    )

# ──────────────────────────────────────────────────────────────────────────────
# 6) PRINT TABLE & SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
print("\n=== Executed Trades ===")
print(trades_df.to_string(index=False))

print("\n=== Summary ===")
tot       = len(trades_df)
total_pnl = trades_df['profit'].sum() if tot else 0.0
win_rate  = (trades_df['profit'] > 0).mean() * 100 if tot else 0.0
avg_pnl   = trades_df['profit'].mean() if tot else 0.0
avg_hold  = trades_df['hold_days'].mean() if tot else 0.0

print(f" Total trades      : {tot}")
print(f" Total PnL         : {total_pnl:.2f}")
print(f" Win rate          : {win_rate:.1f}%")
print(f" Avg PnL/trade     : {avg_pnl:.2f}")
print(f" Avg hold duration : {avg_hold:.0f} days")


# ──────────────────────────────────────────────────────────────────────────────
# 7) PLOT PRICE, EMA, VIDYA & SIGNALS
# ──────────────────────────────────────────────────────────────────────────────
plt.figure(figsize=(14,6))
plt.plot(df.index, df['Close Price  '], label='Close Price')
plt.plot(df.index, strat.ema.array, label=f'EMA({strat.p.ema_period})')
plt.plot(df.index, strat.vidya.vidya.array,
         label=f'VIDYA(period={strat.p.vidya_period},vol={strat.p.vol_period})')

for _, t in trades_df.iterrows():
    plt.scatter(t['entry_date'], t['entry_price'], marker='^', color='green')
    plt.scatter(t['exit_date'],  t['exit_price'],  marker='v', color='red')

plt.title("EMA vs VIDYA Crossover – Buy/Sell Signals")
plt.legend()
plt.tight_layout()
plt.show()
