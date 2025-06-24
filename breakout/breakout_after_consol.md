Here’s the script—save it as `breakout_after_consol.py` next to `scrip.csv`, then install pandas and run:

```bash
pip install pandas
python breakout_after_consol.py --price-lookback 20 --cons-window 10 --long-window 50 --percentile 0.3
```

```python
#!/usr/bin/env python3
import argparse
import pandas as pd

def load_data(path):
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'High Price':  'High',
        'Low Price':   'Low',
        'Close Price': 'Close'
    }, inplace=True)
    return df

def detect_resistance_breakouts(df, lookback):
    df['Resistance'] = (
        df['High']
          .shift(1)
          .rolling(window=lookback, min_periods=1)
          .max()
    )
    df['Price_Breakout'] = df['Close'] > df['Resistance']
    return df

def detect_consolidation(df, cons_window, long_window, percentile):
    # 1. Compute daily range
    df['Range'] = df['High'] - df['Low']
    # 2. Avg range over consolidation window (lagged by 1)
    df['Avg_Range'] = (
        df['Range']
          .shift(1)
          .rolling(window=cons_window, min_periods=1)
          .mean()
    )
    # 3. Squeeze threshold: percentile of avg_range over long window
    df['Cons_Threshold'] = (
        df['Avg_Range']
          .rolling(window=long_window, min_periods=1)
          .quantile(percentile)
          .shift(1)
    )
    # 4. Consolidation flag
    df['Consolidating'] = df['Avg_Range'] < df['Cons_Threshold']
    return df

def main():
    p = argparse.ArgumentParser(description="Breakout after consolidation filter")
    p.add_argument('--csv',            default='scrip.csv', help="Path to scrip.csv")
    p.add_argument('--price-lookback', type=int, default=20, help="Resistance lookback days")
    p.add_argument('--cons-window',    type=int, default=10, help="Consolidation window days")
    p.add_argument('--long-window',    type=int, default=50, help="Long window for threshold")
    p.add_argument('--percentile',     type=float, default=0.3, help="Percentile (0–1) for threshold")
    args = p.parse_args()

    df = load_data(args.csv)
    df = detect_resistance_breakouts(df, args.price_lookback)
    df = detect_consolidation(df, args.cons_window, args.long_window, args.percentile)

    # breakout only after consolidation
    df['Breakout_Consol'] = df['Price_Breakout'] & df['Consolidating']
    bo = df[df['Breakout_Consol']]

    if bo.empty:
        print("No breakouts after consolidation detected.")
    else:
        pd.set_option('display.float_format', '{:.2f}'.format)
        print("Breakouts After Consolidation:\n")
        print(bo[['Close','Resistance','Avg_Range','Cons_Threshold']])

if __name__ == '__main__':
    main()
```

**How it works:**

1. **Resistance**: Highest High over the last `price_lookback` days, excluding today.
2. **Avg\_Range**: The mean daily range (`High–Low`) over the prior `cons_window` days—shifted to avoid lookahead.
3. **Cons\_Threshold**: The `percentile` (e.g. 0.3 for 30th percentile) of `Avg_Range` over the last `long_window` days—also lagged.
4. **Consolidating**: Flags bars where `Avg_Range` is below that threshold (a “squeeze”).
5. **Breakout\_Consol**: True only if we have both a **Price\_Breakout** (close > resistance) **and** a **Consolidating** condition.

Run with your own `--cons-window`, `--long-window`, and `--percentile` to tune how tight a consolidation must be.
