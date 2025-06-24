import pandas as pd
import backtrader as bt
from backtrader.feeds import PandasData

class RealisticBacktestStrategy(bt.Strategy):
    params = (
        ('trade_size', 100),  # Shares per trade
        ('profit_target', 0.05),  # 5% target
        ('stop_loss', 0.02),  # 2% stop
    )

    def __init__(self):
        self.data_open = self.datas[0].open
        self.data_close = self.datas[0].close
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return  # Skip if order pending

        if not self.position:
            # Buy at NEXT OPEN if close > previous close (example condition)
            if self.data_close[0] > self.data_close[-1]:
                self.order = self.buy(exectype=bt.Order.Open)
        else:
            # Exit conditions
            if self.data_close[0] >= self.entry_price * (1 + self.p.profit_target):
                self.order = self.close()
            elif self.data_close[0] <= self.entry_price * (1 - self.p.stop_loss):
                self.order = self.close()

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.entry_price = order.executed.price
                print(f'BUY EXECUTED at OPEN, Price: {order.executed.price:.2f}')
            elif order.issell():
                print(f'SELL EXECUTED at CLOSE, Price: {order.executed.price:.2f}')
        self.order = None

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    
    # Load your specific data format
    data = pd.read_csv('your_data.csv', parse_dates=['Date  '], index_col='Date  ')
    
    # Clean and convert numeric columns (handling commas in Indian number format)
    numeric_cols = ['Open Price  ', 'High Price  ', 'Low Price  ', 'Close Price  ', 'Total Traded Quantity  ']
    for col in numeric_cols:
        data[col] = data[col].astype(str).str.replace(',', '').astype(float)
    
    # Rename columns to Backtrader's expected names
    data = data.rename(columns={
        'Open Price  ': 'open',
        'High Price  ': 'high',
        'Low Price  ': 'low',
        'Close Price  ': 'close',
        'Total Traded Quantity  ': 'volume'
    })
    
    # Add data feed
    data_feed = PandasData(dataname=data)
    cerebro.adddata(data_feed)
    
    # Configure broker
    cerebro.broker.setcash(1000000)  # Increased cash for TCS's high share price
    cerebro.broker.setcommission(commission=0.001)  # 0.1% commission
    
    # Add strategy
    cerebro.addstrategy(RealisticBacktestStrategy)
    
    print('Starting Portfolio Value: ₹%.2f' % cerebro.broker.getvalue())
    results = cerebro.run()
    print('Final Portfolio Value: ₹%.2f' % cerebro.broker.getvalue())
    
    # Plot results
    cerebro.plot()