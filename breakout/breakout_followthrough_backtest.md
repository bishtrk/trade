analyse follow through after breakout: Great! I’ll do three things in this answer:

1. **Explain “Follow-through”** with simple examples.
2. **Show how to check for follow-through in Python** (code).
3. **Show you how to statistically test how often breakouts after consolidation/resistance zones actually sustain, using backtesting logic in Python.**

---

## **1. What is “Follow-through” in Breakouts?**

**Follow-through** means that after a breakout candle (the day price jumps above a resistance/consolidation), the price:

* **Closes near its high** (shows strong buying interest on breakout day), and
* **Does NOT fall back** below the breakout level (the “old range”) in the next few candles/days.

**Why does this matter?**
A breakout with strong follow-through means there is **genuine buying pressure** and market conviction. Weak follow-through (price closes weak, or falls back immediately) is often a “false breakout” or “bull trap.”

### **Visual Example:**

```
Resistance zone:     95–100

Day 1: Closes at 105 (breakout, closes near high)
Day 2: Closes at 109 (follow-through, strong)
Day 3: Closes at 113 (even stronger!)
```

This is **positive follow-through**—the breakout is sustaining.

**Negative example:**

```
Day 1: Closes at 105 (breakout)
Day 2: Falls back, closes at 98 (back inside old range)
```

This is **failed follow-through**—the breakout failed.

---

## **2. Python Example: Checking Follow-Through**

Here’s a workflow you can use to automate the check:

```python
import yfinance as yf
import pandas as pd

# Download data
df = yf.download('RELIANCE.NS', period='6mo')

# Find breakouts above 20-day resistance
window = 20
df['resistance'] = df['High'].rolling(window=window).max().shift(1)
df['is_breakout'] = df['Close'] > df['resistance']

# Find breakout candles
breakouts = df[df['is_breakout']]

# Function to check follow-through (next 3 days)
def check_follow_through(idx, df, breakout_level):
    next_days = df.loc[idx:].iloc[1:4]
    # Condition 1: Next closes never fall below breakout level (no failed follow-through)
    if (next_days['Close'] > breakout_level).all():
        # Condition 2: First breakout closes in top 40% of the day's range
        breakout_candle = df.loc[idx]
        candle_close = breakout_candle['Close']
        day_low, day_high = breakout_candle['Low'], breakout_candle['High']
        threshold = day_low + 0.6 * (day_high - day_low)
        return candle_close >= threshold
    return False

# Analyze all breakouts
results = []
for idx in breakouts.index:
    breakout_level = df.loc[idx, 'resistance']
    if pd.notna(breakout_level) and check_follow_through(idx, df, breakout_level):
        results.append((idx, df.loc[idx, 'Close']))

print(f"Breakouts with positive follow-through: {len(results)}")
for date, close in results:
    print(f"Breakout on {date.date()} at close {close}")
```

---

## **3. Backtest: How Often Do Such Breakouts Succeed?**

Here’s a simple approach:

* Mark all breakouts from resistance/consolidation.
* Check if price is still higher after N days (e.g., 10 days).
* Calculate the percentage of breakouts with positive follow-through.

```python
success_count = 0
total_breakouts = 0
N = 10  # days to check for sustained breakout

for idx in breakouts.index:
    breakout_close = df.loc[idx, 'Close']
    # Check if price is above breakout close after N days
    try:
        future_close = df.loc[idx:].iloc[N]['Close']
        if future_close > breakout_close:
            success_count += 1
        total_breakouts += 1
    except IndexError:
        # Not enough future data, skip
        continue

if total_breakouts > 0:
    success_rate = 100 * success_count / total_breakouts
    print(f"Success rate of breakouts after {N} days: {success_rate:.1f}%")
else:
    print("No breakouts found in this period.")
```

---

## **Summary Table**

| Step                    | What to Check (in Python)                   |
| ----------------------- | ------------------------------------------- |
| Detect breakout         | Close > resistance/consolidation            |
| Positive follow-through | 1) Close near high  2) Stays above breakout |
| Backtest success        | After N days, close > breakout close?       |

---

### **In summary:**

* **Follow-through** is crucial for a sustainable breakout. It means the price closes strong and stays above the breakout zone for at least a few bars.
* You can automate the whole process in Python—detection, follow-through check, and statistical analysis.
* **Typical result**: Only a subset of breakouts will show strong follow-through. These are your “high conviction” setups!

Let me know if you want to see this as a complete script, or want to tweak the parameters for your specific use case!


=======

Below is a self-contained Python script that will:

1. **Detect breakouts above prior resistance**
2. **Check for positive follow-through** (close near high and no fallback over the next few days)
3. **Back-test how often those breakouts sustain** after *N* days

Save it as `breakout_followthrough_backtest.py` in the same folder as your `scrip.csv`, then install dependencies and run it.

```bash
pip install pandas numpy
python breakout_followthrough_backtest.py \
  --csv scrip.csv \
  --price-lookback 20 \
  --follow-days 3 \
  --close-near-pct 0.6 \
  --backtest-days 10
```

```python
#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np

def load_data(path):
    """Load scrip.csv, parse dates, strip commas, rename OHLC columns."""
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

def detect_price_breakouts(df, price_lookback):
    """Flag days where Close > max(High) of prior price_lookback days."""
    df = df.copy()
    df['Resistance'] = (
        df['High']
          .shift(1)
          .rolling(window=price_lookback, min_periods=1)
          .max()
    )
    df['Breakout'] = df['Close'] > df['Resistance']
    return df

def check_follow_through(df, idx, follow_days, close_near_pct):
    """
    Returns True if on breakout day idx:
      1) Close ≥ Low + close_near_pct*(High−Low)
      2) In the next follow_days, all Closes remain > Resistance level
    """
    res = df.at[idx, 'Resistance']
    high, low, close = df.at[idx, 'High'], df.at[idx, 'Low'], df.at[idx, 'Close']
    # 1) closed in the top (1 − close_near_pct) portion of that bar
    if close < low + close_near_pct * (high - low):
        return False
    # 2) no fallback in the next follow_days bars
    window = df.loc[idx:].iloc[1:follow_days+1]
    if window.empty:
        return False
    return (window['Close'] > res).all()

def backtest_sustain(df, breakout_dates, backtest_days):
    """
    Returns (total, follow_through_count, sustain_count):
    - total breakouts
    - how many had positive follow-through
    - how many were still above breakout Close after backtest_days
    """
    total = 0
    ft_ok = 0
    sustain = 0

    for idx in breakout_dates:
        total += 1
        res = df.at[idx, 'Resistance']
        b_close = df.at[idx, 'Close']

        if check_follow_through(df, idx, args.follow_days, args.close_near_pct):
            ft_ok += 1

        # check N-day later close
        future = df.loc[idx:].iloc[backtest_days:backtest_days+1]
        if not future.empty and future['Close'].iat[0] > b_close:
            sustain += 1

    return total, ft_ok, sustain

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="Breakout + Follow-through + Backtest on TCS")
    p.add_argument('--csv',            default='scrip.csv',    help="Path to scrip.csv")
    p.add_argument('--price-lookback', type=int, default=20, help="Days for resistance lookback")
    p.add_argument('--follow-days',    type=int, default=3,  help="Days to check no-fallback after breakout")
    p.add_argument('--close-near-pct', type=float, default=0.6,
                   help="Close must be in top (1−pct) of candle (e.g. 0.6 = top 40%%)")
    p.add_argument('--backtest-days',  type=int, default=10,
                   help="Days forward to test if Close > breakout Close")
    args = p.parse_args()

    # 1. Load & detect breakouts
    df = load_data(args.csv)
    df = detect_price_breakouts(df, args.price_lookback)
    bo_dates = df.index[df['Breakout']]

    if bo_dates.empty:
        print("No breakouts detected.")
        exit()

    # 2. Compute metrics
    total, ft_ok, sustain = backtest_sustain(
        df, bo_dates, args.backtest_days
    )

    # 3. Print results
    print(f"Total breakouts found: {total}")
    print(f"→ Positive follow-through ({args.follow_days}d, top {int((1-args.close_near_pct)*100)}%): {ft_ok}")
    print(f"→ Sustained after {args.backtest_days} days: {sustain}")
    print(f"Follow-through rate: {ft_ok/total*100:.1f}%")
    print(f"Sustain rate:      {sustain/total*100:.1f}%")
```

### How It Works

1. **Price Breakouts**

   * Computes a **rolling maximum** of `High` over the prior `--price-lookback` days (shifted by 1) as `Resistance`.
   * Flags days where `Close > Resistance`.

2. **Follow-Through Check**

   * **Closes near its high**: `Close ≥ Low + close_near_pct×(High–Low)`.
   * **No fallback**: in the next `--follow-days`, all closing prices stay above the `Resistance` level.

3. **Back-Test Sustain**

   * For each breakout, checks if the price is still above the **breakout Close** after `--backtest-days`.
   * Reports total breakouts, how many had positive follow-through, and how many sustained past N days, plus percentages.

Feel free to tweak any of the parameters via the command line to suit your style and TCS’s behavior.
