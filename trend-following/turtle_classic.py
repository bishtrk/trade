import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt

# 1) Load & clean data
df = pd.read_csv('scrip.csv', dtype=str)
df['Date  '] = pd.to_datetime(df['Date  '].str.strip(), format='%d-%b-%Y')
df.set_index('Date  ', inplace=True)

for col in ['Open Price  ', 'High Price  ', 'Low Price  ',
            'Close Price  ', 'Total Traded Quantity  ']:
    df[col] = df[col].str.replace(',', '').astype(float)

# 2) Long-only Turtle Strategy (20-day entry, 10-day exit)
class LongTurtle(bt.Strategy):
    params = dict(entry_period=20, exit_period=10)

    def __init__(self):
        # Donchian channels
        self.high20 = bt.ind.Highest(self.data.high, period=self.p.entry_period)
        self.low10  = bt.ind.Lowest(self.data.low,  period=self.p.exit_period)
        # Temp storage for a single open trade
        self._open = {}
        self.trades = []

    def next(self):
        # 1) Not in a position → check for long entry
        if not self.position:
            # today's close > yesterday's 20-day high → enter long
            if self.data.close[0] > self.high20[-1]:
                self.buy(size=1)

        # 2) If long → check for exit on 10-day low
        else:
            if self.data.close[0] < self.low10[-1]:
                self.close()

    def notify_order(self, order):
        if order.status != order.Completed:
            return

        dt    = bt.num2date(order.executed.dt).date()
        price = order.executed.price

        # Entry
        if order.isbuy() and not self._open:
            self._open = {
                'entry_date' : dt,
                'entry_price': price
            }
        # Exit
        elif order.issell() and self._open:
            self._open.update({
                'exit_date'  : dt,
                'exit_price' : price,
                'profit'     : price - self._open['entry_price'],
                'profit_pct' : (price - self._open['entry_price'])
                               / self._open['entry_price'] * 100
            })
            self.trades.append(self._open)
            self._open = {}

# 3) Backtest setup & run
cerebro = bt.Cerebro()
cerebro.addstrategy(LongTurtle)

data = bt.feeds.PandasData(
    dataname=df,
    open='Open Price  ',
    high='High Price  ',
    low='Low Price  ',
    close='Close Price  ',
    volume='Total Traded Quantity  ',
    openinterest=None
)
cerebro.adddata(data)
cerebro.broker.setcash(100000)

strat = cerebro.run()[0]

# 4) Build trades DataFrame and compute hold_days
trades_df = pd.DataFrame(strat.trades)
if not trades_df.empty:
    trades_df['hold_days'] = trades_df.apply(
        lambda r: (r['exit_date'] - r['entry_date']).days, axis=1
    )
else:
    trades_df = pd.DataFrame(columns=[
        'entry_date','entry_price','exit_date','exit_price',
        'profit','profit_pct','hold_days'
    ])

# 5) Print trades and summary
print("\n=== Executed Trades ===")
print(trades_df.to_string(index=False))

tot   = len(trades_df)
pnl   = trades_df['profit'].sum() if tot else 0.0
win   = (trades_df['profit'] > 0).mean()*100 if tot else 0.0
avg_p = trades_df['profit'].mean() if tot else 0.0
avg_h = trades_df['hold_days'].mean() if tot else 0.0

print("\n=== Summary ===")
print(f" Total trades      : {tot}")
print(f" Total PnL         : {pnl:.2f}")
print(f" Win rate          : {win:.1f}%")
print(f" Avg PnL/trade     : {avg_p:.2f}")
print(f" Avg hold duration : {avg_h:.0f} days")

# 6) (Optional) plot close price with long entry/exit markers
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Close Price  '], label='Close Price')
for _, r in trades_df.iterrows():
    plt.scatter(r['entry_date'], r['entry_price'], marker='^', color='green', label='Entry')
    plt.scatter(r['exit_date'],  r['exit_price'],  marker='v', color='red',   label='Exit')
plt.title("Long-Only Turtle Strategy (20/10) Entries & Exits")
plt.legend(loc='best')
plt.tight_layout()
plt.show()