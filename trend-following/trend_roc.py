import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt

# 1. Load & preprocess CSV
df = pd.read_csv('scrip.csv', dtype=str)
df['Date  '] = pd.to_datetime(df['Date  '].str.strip(), format='%d-%b-%Y')
df.set_index('Date  ', inplace=True)

num_cols = [
    'Prev Close  ', 'Open Price  ', 'High Price  ',
    'Low Price  ',  'Last Price  ', 'Close Price  ',
    'Average Price ', 'Total Traded Quantity  '
]
for col in num_cols:
    df[col] = df[col].str.replace(',', '').astype(float)

# 2. Strategy using notify_order
class RocMomentum(bt.Strategy):
    params = dict(roc_period=20)
    def __init__(self):
        self.roc   = bt.indicators.ROC(self.data.close, period=self.p.roc_period)
        self.cross = bt.ind.CrossOver(self.roc, 0)
        self.current = {}
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
            self.current = {'entry_date': dt, 'entry_price': price}
        elif order.issell():
            self.current.update({
                'exit_date':   dt,
                'exit_price':  price,
                'profit':      price - self.current['entry_price'],
                'profit_pct':  (price - self.current['entry_price']) / self.current['entry_price'] * 100
            })
            self.trades.append(self.current)
            self.current = {}

# 3. Run backtest
cerebro = bt.Cerebro()
cerebro.addstrategy(RocMomentum, roc_period=20)
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

# 4. Build trades DataFrame & convert hold_duration to days only
trades_df = pd.DataFrame(strat.trades)
trades_df['hold_duration'] = (trades_df['exit_date'] - trades_df['entry_date']).apply(lambda td: td.days)

print("\nExecuted Trades:")
print(trades_df.to_string(index=False))

# 5. Summary using days only
total_trades = len(trades_df)
total_pnl    = trades_df['profit'].sum()
win_rate     = (trades_df['profit'] > 0).mean() * 100
avg_pnl      = trades_df['profit'].mean()
avg_hold     = trades_df['hold_duration'].mean() if total_trades else 0

print("\nSummary:")
print(f" Total trades:      {total_trades}")
print(f" Total PnL:         {total_pnl:.2f}")
print(f" Win rate:          {win_rate:.1f}%")
print(f" Avg PnL/trade:     {avg_pnl:.2f}")
print(f" Avg hold duration: {avg_hold:.0f} days")

# 6. Combined chart: price+volume above, ROC below
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 8))

# Price & volume
ax1.plot(df.index, df['Close Price  '], label='Close Price')
ax1_t = ax1.twinx()
ax1_t.bar(df.index, df['Total Traded Quantity  '], alpha=0.3)
for _, r in trades_df.iterrows():
    ax1.plot(r['entry_date'], r['entry_price'], '^', color='green')
    ax1.plot(r['exit_date'],  r['exit_price'],  'v', color='red')
ax1.set_title("Price & Volume with Buy/Sell Signals")

# ROC
roc = df['Close Price  '].pct_change(periods=20) * 100
ax2.plot(df.index, roc, label='20-Day ROC')
ax2.axhline(0, color='black', lw=0.5)
ax2.set_title("20-Day Rate of Change (ROC)")

plt.tight_layout()
plt.show()
