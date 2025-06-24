Below is a deeper look at the **ATR-Based Dynamic Breakout** concept, followed by a self-contained script you can run on your system.

---

## **4. ATR-Based Dynamic Breakout**

### **What It Is**

Rather than using an absolute price threshold (like prior resistance), you define a breakout by a **relative volatility** measure: today’s price movement must exceed a multiple of the recent ATR. You can measure movement either as:

1. **True range**: `High – Low`
2. **Net move**: `|Close – Open|`

### **Why It Works**

* Stocks have different “typical” daily swings. ATR tells you that historic average.
* A 1-point swing in a low-volatility name (ATR ≈1) is as meaningful as a 5-point swing in a choppy name (ATR ≈5).
* Focusing on “biggest” moves relative to normal range filters out noise and highlights genuine breakouts.

### **Key Parameters**

* **ATR look-back** (`n`): number of days to average True Range (14 is standard).
* **Multiplier** (`k`): how many ATRs define a “big move” (common: 1.5–2).
* **Mode**: decide whether to compare **range** (`High–Low`) or **net** (`|Close–Open|`) to `k×ATR`.

---

## **Script: `atr_dynamic_breakout.py`**

Save this alongside `scrip.csv`, install pandas, then run:

```bash
pip install pandas
python atr_dynamic_breakout.py --mode range --atr-period 14 --multiplier 2.0
```

```python
#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np

def load_data(path):
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'High Price':  'High',
        'Low Price':   'Low',
        'Open Price':  'Open',
        'Close Price': 'Close'
    }, inplace=True)
    return df

def compute_atr(df, period):
    """Compute N-day ATR (Average True Range)."""
    hl = df['High'] - df['Low']
    hc = (df['High'] - df['Close'].shift(1)).abs()
    lc = (df['Low']  - df['Close'].shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(window=period, min_periods=1).mean()

def detect_dynamic_breakouts(df, mode, atr_period, multiplier):
    df['ATR'] = compute_atr(df, atr_period)
    if mode == 'range':
        df['Move'] = df['High'] - df['Low']
    else:  # 'net'
        df['Move'] = (df['Close'] - df['Open']).abs()
    df['Breakout_ATR'] = df['Move'] > multiplier * df['ATR']
    return df

def main():
    p = argparse.ArgumentParser(description="ATR-Based Dynamic Breakout Detector")
    p.add_argument('--csv',         default='scrip.csv',    help="Path to scrip.csv")
    p.add_argument('--mode',        choices=['range','net'], default='range',
                   help="Compare ATR to High–Low ('range') or |Close–Open| ('net')")
    p.add_argument('--atr-period',  type=int, default=14,    help="ATR look-back period")
    p.add_argument('--multiplier',  type=float, default=2.0, help="ATR multiple for breakout")
    args = p.parse_args()

    df = load_data(args.csv)
    df = detect_dynamic_breakouts(df, args.mode, args.atr_period, args.multiplier)

    bo = df[df['Breakout_ATR']]
    if bo.empty:
        print("No ATR-based dynamic breakouts found.")
    else:
        pd.set_option('display.float_format', '{:.2f}'.format)
        print(f"ATR-Based Breakouts (mode={args.mode}, atr={args.atr_period}, mult={args.multiplier}):\n")
        print(bo[['High','Low','Open','Close','Move','ATR']].to_string())

if __name__ == '__main__':
    main()
```

### **How It Works**

1. **Load Data**: Reads and cleans the OHLC series.
2. **Compute ATR**: Uses the max of `(High–Low, High–PrevClose, Low–PrevClose)` over a rolling window.
3. **Measure Today’s Move**:

   * **`range`**: `High – Low`
   * **`net`**: `|Close – Open|`
4. **Flag Breakout**: `Move > multiplier × ATR`.
5. **Output**: Lists all dates where that condition holds.

Tweak `--atr-period` and `--multiplier` to suit TCS’s typical volatility or your style—higher `multiplier` yields fewer, stronger breakouts.
