Below is a self-contained Python script that:

1. **Loads** your `scrip.csv` data.
2. **Computes “prior resistance”** as the highest High over the last `N` days (shifted by one to exclude today).
3. **Flags breakout days** where the current Close exceeds that resistance.
4. **Prints** out the breakout dates with their Close and resistance levels.

Save as `breakout_resistance.py` next to your `scrip.csv`, then run:

```bash
pip install pandas
python breakout_resistance.py --lookback 20
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
        'Close Price': 'Close'
    }, inplace=True)
    return df

def find_breakouts(df, lookback):
    # rolling max of High over prior lookback days, shifted by 1
    df['Resistance'] = df['High'].shift(1).rolling(window=lookback, min_periods=1).max()
    # breakout when Close exceeds that resistance
    df['Breakout'] = df['Close'] > df['Resistance']
    return df

def main():
    p = argparse.ArgumentParser(description="Detect breakouts above previous resistance in TCS data")
    p.add_argument('--csv',       default='scrip.csv',          help="Path to your scrip.csv file")
    p.add_argument('--lookback',  type=int,  default=20,       help="Look-back period for resistance (days)")
    args = p.parse_args()

    df = load_data(args.csv)
    df = find_breakouts(df, args.lookback)

    # extract breakout days
    bo = df[df['Breakout']]
    if bo.empty:
        print("No breakouts detected.")
    else:
        print(f"Breakouts above {args.lookback}-day resistance:\n")
        print(bo[['Close','Resistance']].to_string(formatters={
            'Close':      '{:,.2f}'.format,
            'Resistance': '{:,.2f}'.format
        }))

if __name__ == '__main__':
    main()
```

---

### How It Works

* **Resistance**:

  ```python
  df['Resistance'] = (
      df['High']
        .shift(1)                              # exclude current bar
        .rolling(window=lookback)
        .max()
  )
  ```
* **Breakout condition**:

  ```python
  df['Breakout'] = df['Close'] > df['Resistance']
  ```
* **Key points**:

  * **`shift(1)`** makes sure you compare today’s close against **prior** highs.
  * **`rolling(max)`** over `lookback` days defines how “long-term” the resistance level is.

Run with different `--lookback` values to tune how many days of peaks you consider “resistance.”
