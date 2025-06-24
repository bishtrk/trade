For a “buy-at-CMP” trade, you’d feed exactly the same DataFrame of past TCS prices into the clustering+volatility routine and pick parameter values that reflect how far back you want to look for your breakout and your support zone, plus how tight or loose you want your buffers.

Here’s what you’ll supply:

| Parameter              | What it Means                                                                                            | Typical Value for a Swing Trade |
| ---------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------- |
| **breakout\_lookback** | How many days back to scan for “new highs” that qualify as breakouts (identifies all your entry signals) | 20                              |
| **support\_window**    | How many days (prior to each breakout) you inspect for local minima                                      | 10                              |
| **local\_order**       | How many bars on each side to compare when flagging a local minimum (e.g. Low\[i] < Low\[i±1…order])     | 2                               |
| **tol\_pct**           | Clustering tolerance for minima (group all dips within ±tol\_pct × entry\_price)                         | 0.5%  (0.005)                   |
| **buffer\_pct**        | Fixed buffer as a % of entry price to avoid whipsaws                                                     | 0.5%  (0.005)                   |
| **atr\_period**        | Look-back for your Average True Range calculation (volatility)                                           | 14                              |

---

### Putting it together

1. **Load** your historical TCS OHLCV into `df`.

2. **Call**:

   ```python
   stops = compute_stop_levels_localmin(
     df,
     breakout_lookback=20,
     support_window=10,
     local_order=2,
     tol_pct=0.005,
     buffer_pct=0.005,
     atr_period=14
   )
   ```

3. **Extract** the row for the breakout date that corresponds to your CMP entry (or simply the last row if you treat today as a breakout). That row’s `StopPrice` is your suggested stop.

---

#### Example

If you bought at the close on **2025-06-20**:

```python
entry_date = pd.Timestamp('2025-06-20')
stop = stops.loc[entry_date, 'StopPrice']
print(f"Stop-loss for entry on {entry_date.date()}: ₹{stop:.2f}")
```

---

**Why these defaults?**

* 20 days for breakouts gives you enough history to spot recent highs.
* A 10 day support window focuses on the most relevant dips.
* `local_order=2` weeds out tiny two-bar flickers.
* 0.5% tolerance and buffer balance noise-rejection with a reasonably tight stop.
* ATR 14 ensures your buffer always respects prevailing volatility.

Feel free to tweak any of these—wider lookbacks or larger buffers—to suit your personal style and the typical daily range of TCS.


---

You’re absolutely right—when you’re buying at a live market price (CMP) rather than on one of our “breakout” signals, you need to use **your actual entry price** as the reference for both the **tolerance** (for clustering) and the **buffer** (for volatility).

Below is a small helper you can drop into your notebook or script. It:

1. **Takes your entry date** (or uses “today” if you just bought at the last available bar).
2. **Takes your actual entry price** (the CMP you paid).
3. **Finds all local minima** in the preceding support window.
4. **Clusters** them within ±`tol_pct * entry_price`.
5. **Computes** an ATR‐based buffer using your `atr_period` and also a fixed `buffer_pct * entry_price`.
6. **Returns** the stop‐loss price = `support_min_of_cluster – buffer`.

```python
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

def compute_atr(df, period=14):
    hl = df['High'] - df['Low']
    hc = (df['High'] - df['Close'].shift(1)).abs()
    lc = (df['Low']  - df['Close'].shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(period, min_periods=1).mean()

def find_local_minima(series, order=2):
    mask = pd.Series(True, index=series.index)
    for i in range(1, order+1):
        mask &= (series < series.shift(i)) & (series < series.shift(-i))
    return mask

def calculate_stop_from_entry(
    df,
    entry_date,       # e.g. pd.Timestamp('2025-06-20')
    entry_price,      # your actual buy price, e.g. 3435.70
    support_window=10,
    local_order=2,
    tol_pct=0.005,    # cluster tolerance = 0.5% of entry_price
    buffer_pct=0.005, # buffer = 0.5% of entry_price
    atr_period=14
):
    # 1. Ensure Date index
    df = df.copy()
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
        df.set_index('Date', inplace=True)
    df = df.sort_index()

    # 2. Compute ATR
    df['ATR'] = compute_atr(df, period=atr_period)

    # 3. Look at the N bars immediately before your entry
    window = df.loc[:entry_date].iloc[-support_window-1:-1]
    lows   = window['Low']

    # 4. Find local minima in that window
    minima_mask = find_local_minima(lows, order=local_order)
    minima_vals = lows[minima_mask].tolist()

    # 5. Cluster minima within tol_pct * entry_price
    tol_abs = tol_pct * entry_price
    if minima_vals:
        sorted_vals = sorted(minima_vals)
        clusters = []
        current = [sorted_vals[0]]
        for v in sorted_vals[1:]:
            if abs(v - current[0]) <= tol_abs:
                current.append(v)
            else:
                clusters.append(current)
                current = [v]
        clusters.append(current)
        # pick the cluster with most members
        best_cluster = max(clusters, key=len)
        support_min = min(best_cluster)
    else:
        # fallback: lowest low in the window
        support_min = lows.min()

    # 6. Compute buffer = max(buffer_pct*entry_price, ATR on entry_date)
    atr_at_entry = df.at[entry_date, 'ATR']
    buffer = max(buffer_pct * entry_price, atr_at_entry)

    # 7. Final stop price
    stop_price = support_min - buffer
    return {
        'entry_date': entry_date,
        'entry_price': entry_price,
        'support_min': support_min,
        'atr_at_entry': atr_at_entry,
        'buffer_used': buffer,
        'stop_price': stop_price
    }

# ——— USAGE EXAMPLE ———

# 1) Load your TCS data
df = pd.read_csv('scrip.csv', thousands=',')
df.rename(columns={
    'Open Price':'Open','High Price':'High',
    'Low Price':'Low','Close Price':'Close'
}, inplace=True)

# 2) Suppose you bought today at CMP 3435.70 on 2025-06-20
entry_date  = pd.Timestamp('2025-06-20')
entry_price = 3435.70

result = calculate_stop_from_entry(
    df,
    entry_date=entry_date,
    entry_price=entry_price,
    support_window=10,
    local_order=2,
    tol_pct=0.005,
    buffer_pct=0.005,
    atr_period=14
)

print("Stop‐Loss Calculation:")
for k,v in result.items():
    if isinstance(v, float):
        print(f"  {k:12s} = {v:,.2f}")
    else:
        print(f"  {k:12s} = {v}")
```

**Key point:**

* We use **your actual entry price** (`entry_price`) as the basis for:

  * **Clustering tolerance** (`tol_pct * entry_price`)
  * **Fixed buffer** (`buffer_pct * entry_price`)
* We still use ATR (on your entry date) to ensure the buffer isn’t tighter than recent volatility.

That gives you a single `stop_price` designed for a blind buy at CMP—anchored both to recent support structure and to your own entry price.
