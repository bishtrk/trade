yes, the ideas is i want to screen stocks which are up certain percentage suddenly. usually there is a reason behind such jumps like a news or something. and i want to capture such breakstocks because they might just start their upwaard journey. at same time i want to reduce risk of false breakouts so that i am not stuck at a high. one way is to see if follow through buying is happening or not. this is why i created this script. but not whether this was correctly captured in the script. Got it ?


---

Exactly—your goal is to find stocks that:

1. **Jump a minimum % above their recent high** (e.g. 5–10%),
2. **Do it on strong volume**, and
3. **Show follow-through buying** over the next few days so you’re not just buying a one-day spike.

Your script now captures that by:

* Using `--break-pct` to require `Close/Resistance – 1 ≥ break_pct` (so only “zoom” breakouts make the list).
* Computing `Avg_Volume` and flagging true volume spikes (you can even filter out any breakout where `HighVol==False`).
* Checking that the candle closed in its top-pct (your `--pct`) of the bar and that the next N days all stayed above the breakout level.

---

### A few quick tweaks to tighten it further

* **Enforce the volume surge** at signal time:

  ```python
  df['Breakout'] = (df['Pct_Above_Res'] >= min_break_pct) \
                   & (df['Volume'] > df['Avg_Volume'] * vol_multiplier)
  ```

* **Capture gap-ups at the open** (news breakouts often gap open):

  ```python
  df['GapPct'] = df['Open'] / df['Close'].shift(1) - 1
  df['Breakout'] &= df['GapPct'] >= min_gap_pct
  ```

* **Validate on a known example**: pick a stock/date where you know there was news, run the script, and manually verify the date appears in your table.

With those in place, you’ll be screening only for **big, high-volume jumps** that also **hold above their new range**, which is exactly what you described. Let me know if you want code snippets for any of those tweaks!


---

This little script is essentially a **proof-of-concept momentum screener** and backtester rolled into one. In practical terms, you can think of it as a template for:

1. **Signal Generation**

   * It scans your historical price data and flags every time the close “clears” its recent *N*-day high (the basic breakout).
   * It then filters only those breakouts that close in the upper portion of their own bar (your “follow-through”) and checks whether price stays above the breakout level after *M* days.

2. **Quick Backtest & Metrics**

   * You immediately get a sense of how often those signals actually showed follow-through (did the candle close strongly?) and how many of them still finished higher after *M* more days.
   * All the metrics and a detailed table print out in your console, so you can eyeball which dates “worked” and which didn’t.

3. **Visualization**

   * Finally it plots price + volume with your breakout and follow-through markers, so you can visually inspect the setups.

---

## Why you’re seeing \~50/50 results

A simple “break above the last 20-day high” strategy with only a candle-top check is **extremely basic**—it captures **any** churn that just happens to poke above a rolling high. In most markets, roughly half of these pokes will fail to develop further momentum, and half will succeed, so seeing \~50% follow-through or sustain is actually pretty typical.

---

## When this becomes useful

* **Screening, not trading**: Use it to **short-list** candidates, then layer on more filters (e.g. relative strength, sector momentum, fundamental screens).
* **Parameter exploration**: Try different lookbacks (10, 30, 60 days), different “follow-through” thresholds (e.g. close in top 20% of range rather than 40%), or require a minimum % breakout above the prior high (e.g. 1–2%).
* **Combine signals**: Pair your breakouts with trend filters (e.g. price > 200-day MA), volatility filters (e.g. ATR squeeze), or volume spikes (e.g. today’s volume > 2× recent average).
* **Risk & money management**: Add stop-loss rules, position sizing, and profit targets in your backtest to see if risk-adjusted returns become attractive.

---

### Next steps

1. **Tighten your entry**

   * Require a bigger % move beyond the high.
   * Only trade breakouts that occur when overall market or sector is trending up.

2. **Improve your filter**

   * Use a moving-average trend filter (e.g. only breakouts above the 50- or 200-day MA).
   * Add an RSI or MACD confirmation so you’re not buying overbought breakouts.

3. **Expand your universe**

   * Run the same script across hundreds of stocks or ETFs and look for clusters of high follow-through rates.
   * Compare different lookback settings side-by-side.

4. **Rigorous backtest**

   * Integrate it into a full backtesting engine (like Backtrader) with entry/exit rules and P/L tracking—right now you’re only measuring raw signal success, not net returns after slippage, commissions, and drawdowns.

By itself, the simple “20-day high” check isn’t a silver bullet. But as a **building block**—something you can tweak, combine, and rigorously backtest—it’s a great way to explore momentum patterns and learn how signal filters actually affect performance.


-------
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
