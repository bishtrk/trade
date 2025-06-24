Here’s a deeper dive into each of those advanced breakout filters—what they look for, why they work, and when you’d use them:

---

## 1. Breakout Above Previous Resistance

**What it is**

* You define “resistance” as the highest High over some look-back (e.g. 20 days).
* A breakout occurs when the current Close (or High) exceeds that level.

**Why it works**

* Institutional and technical traders often place sell orders at prior peaks.
* Piercing that ceiling shows fresh buying interest strong enough to clear those standing orders.

**Key considerations**

* **Look-back length** controls how “long-term” your resistance is.
* Shifting the rolling max by one bar ensures you’re testing against “prior” highs, not today’s.

---

## 2. Volume Confirmation

**What it is**

* You require today’s Volume to exceed a multiple (e.g. 1.5×) of its recent average (say past 20 days).
* Only tag a breakout if it’s supported by abnormally high turnover.

**Why it works**

* High volume signals genuine conviction. Low-volume breakouts often fizzle into “false breakouts.”
* Helps filter out moves driven by a handful of trades or quiet‐market spikes.

**Key considerations**

* Choose your volume multiple: higher (2×) = fewer signals, stronger conviction; lower (1.2×) = more signals, more noise.
* Make sure you use a lagged average (shifted) so you’re not comparing today’s volume to itself.

---

## 3. Breakout After Consolidation

**What it is**

* First identify periods of **low volatility** or sideways action—e.g. average true range over 10 days is in the bottom 30% of its own longer history.
* Only call a breakout valid if it follows such a squeeze.

**Why it works**

* Breakouts from tight ranges tend to be more explosive (think coiled spring).
* Avoids chasing breakouts in already-trending or noisy markets where “continuation” isn’t as meaningful.

**Key considerations**

* Your consolidation window and percentile threshold determine how tight a squeeze must be.
* Too strict → very few breakouts; too loose → little benefit over other filters.

---

## 4. ATR-Based Dynamic Breakout

**What it is**

* Define a breakout not by absolute price but by **relative volatility**: e.g. today’s range (High−Low) or close-to-close move exceeds 2× ATR.

**Why it works**

* Adapts to each stock’s “normal” daily move. A 1-point move on a low-volatility name can be as significant as a 5-point move on a choppier one.
* Filters for the biggest relative swings.

**Key considerations**

* Choose your ATR look-back (14 is standard).
* Decide if you use range (High−Low) or net move (Close−Open) to compare against ATR.

---

## 5. Candle-Pattern Confirmation (Optional)

**What it is**

* Use candlestick patterns—bullish engulfing, marubozu, pierced line—to confirm that the breakout bar itself looks “strong.”

**Why it works**

* Adds a visual/momentum layer: e.g. a bullish engulfing candle closing above resistance is a more emphatic signal than a small body breakout.

**Key considerations**

* Requires a pattern library (TA-Lib, pandas\_ta, etc.).
* Patterns can overlap—decide which ones matter most for your style.

---

## Putting It All Together: A Robust Breakout Filter

1. **Price Filter**: Close crosses above N-day rolling high.
2. **Volume Filter**: Today’s volume > M × its N-day average.
3. **Volatility Filter**: Today’s range (or Close-Open) > K × ATR.
4. **Consolidation Filter** (optional): The prior N-day ATR is in its bottom X-percentile.
5. **Pattern Filter** (optional): The breakout bar is a recognized bullish pattern.

Each additional filter narrows your signals but increases the likelihood that each one represents a **real** breakout with follow-through potential.

---

### When to Use Which

* **All-in** (1 + 2 + 4 + 3): Very high-confidence signals, but rare.
* **Lightweight** (1 + 2): Good balance—price + volume confirm most genuine breakouts.
* **Fast-and-loose** (1 only): Good for scanning many symbols quickly, then eyeballing charts before entry.

---

By layering these logically—price, volume, volatility, consolidation, and pattern—you’ll systematically sieve out noise and focus on breakouts that matter.

===

Below is a two-part solution:

---

## 1. How It Works

1. **Load TCS Data**
   Read your `scrip.csv`, parse dates, set the index, and clean up column names.

2. **Compute Indicators**

   * **SMA**: 20-day simple moving average of Close.
   * **RSI** (14-day), **Stochastic K/D** (14,3,3), and **MACD** (12,26,9) via `pandas_ta`.

3. **Detect Breakouts & Overbought**

   * Define **resistance** as the prior 20-day rolling max of High (shifted by one).
   * A **breakout** is when Close > that resistance.
   * An **overbought breakout** is a breakout day where **any** of these is true:

     * RSI > 70
     * Stoch K > 80
     * Stoch D > 80

4. **Plot Everything** with **mplfinance**:

   * **Price Panel**: Candlesticks + Volume + 20-day SMA + markers for overbought breakouts.
   * **Second Panel**: RSI line + overbought line at 70.
   * **Third Panel**: Stoch K/D lines + overbought band at 80.
   * **Fourth Panel**: MACD line, signal line, and histogram.

---

## 2. Script: `plot_breakout_indicators.py`

```python
#!/usr/bin/env python3
import pandas as pd
import pandas_ta as ta
import mplfinance as mpf
import numpy as np

# 1. Load & prepare data
df = pd.read_csv('scrip.csv', thousands=',')
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
df.set_index('Date', inplace=True)
df.rename(columns={
    'High Price':            'High',
    'Low Price':             'Low',
    'Open Price':            'Open',
    'Close Price':           'Close',
    'Total Traded Quantity': 'Volume'
}, inplace=True)

# 2. Compute SMA
df['SMA20'] = df['Close'].rolling(20).mean()

# 3. Compute breakout signal
df['Resistance20'] = df['High'].shift(1).rolling(20).max()
df['Breakout'] = df['Close'] > df['Resistance20']

# 4. Compute indicators
df['RSI14'] = ta.rsi(df['Close'], length=14)
stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3)
df[['STOCHK','STOCHD']] = stoch[['STOCHk_14_3_3','STOCHd_14_3_3']]
macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
df[['MACD','MACD_SIGNAL','MACD_HIST']] = macd[['MACD_12_26_9','MACDs_12_26_9','MACDh_12_26_9']]

# 5. Flag overbought breakouts
df['OverboughtBreakout'] = (
    df['Breakout'] &
    (
      (df['RSI14']   > 70) |
      (df['STOCHK']  > 80) |
      (df['STOCHD']  > 80)
    )
)

# 6. Prepare mplfinance panels
# Price + SMA + breakout markers
price_apds = [
    mpf.make_addplot(df['SMA20'], color='blue', width=1),
    mpf.make_addplot(
        df['Close'].where(df['OverboughtBreakout']),
        type='scatter', marker='^', markersize=100, color='red'
    )
]

# RSI panel
rsi_apd = mpf.make_addplot(df['RSI14'], panel=1, ylabel='RSI')
rsi_signal = mpf.make_addplot(
    pd.Series(70, index=df.index), panel=1, color='gray', linestyle='--'
)

# Stochastic panel
sto_apd_k = mpf.make_addplot(df['STOCHK'], panel=2, ylabel='Stoch')
sto_apd_d = mpf.make_addplot(df['STOCHD'], panel=2, color='orange')
sto_signal = mpf.make_addplot(
    pd.Series([80,20], index=df.index).T,
    panel=2, color='gray', linestyle='--'
)

# MACD panel
macd_apd = mpf.make_addplot(df['MACD'],      panel=3, ylabel='MACD')
signal_apd = mpf.make_addplot(df['MACD_SIGNAL'], panel=3, color='orange')
hist_apd   = mpf.make_addplot(df['MACD_HIST'],   panel=3, type='bar', width=0.7, alpha=0.5)

all_apds = price_apds + [rsi_apd, rsi_signal, sto_apd_k, sto_apd_d, sto_signal, macd_apd, signal_apd, hist_apd]

# 7. Plot
mpf.plot(
    df,
    type='candle',
    style='charles',
    volume=True,
    addplot=all_apds,
    figratio=(16,9),
    figscale=1.2,
    panel_ratios=(6,2,2,2),
    title='TCS: Price+SMA20 with Overbought Breakouts & Indicators',
    tight_layout=True
)
```

### What You’ll See

* **Main chart**: Candlesticks overlaid with the 20-day SMA (blue) and red `^` markers where an overbought breakout occurred.
* **Panel 1 (RSI)**: RSI line and dashed line at 70.
* **Panel 2 (Stochastics)**: %K and %D lines with an 80/20 zone.
* **Panel 3 (MACD)**: MACD, signal, and histogram bars.
* **Volume**: Shown under the main price panel.

This gives you an instant, visual sense of:

* When price breaks out and whether it’s “too hot” (overbought).
* How momentum indicators support or warn against chasing the move.
* Where the SMA20 is relative to price (trend context).
