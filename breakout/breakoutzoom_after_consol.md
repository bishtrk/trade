Coil → Zoom

Assume the last cons-days were your coil.

Compute the maximum close over that window (the top of the coil).

Flag any day that closes at least zoom-pct above that.

Pros: Very simple, only two parameters.

Cons: Doesn’t verify that volatility was actually low—might flag noisy “thrusts.”

---

Quickly surface any stock that suddenly jumps X% above its recent highs, assuming it had been coiling. Ideal for very fast scans across hundreds of tickers when you just care about a big % move.	

A stock quietly trading in a 50-day range, then gaps and closes 10% above that range.



---
The **`Max_Close`** column is simply the **highest closing price** over the prior **`N`** days (where `N` is your `--cons-days` value), **excluding today**. In other words:

1. You take a rolling window of length `cons_days` over the **`Close`** series.
2. Within each window you pick the **maximum** value.
3. You then shift that series down by one so that, on day *t*, `Max_Close[t]` reflects the maximum close from days *t–N* through *t–1*.

This `Max_Close` represents the top of your “coil” (consolidation zone). When today’s close exceeds `(Max_Close × (1 + zoom_pct))`, you know price has “zoomed” out of that zone by at least your threshold.

---

Let me unpack each of your questions:

---

### 1) “Low-volatility coiling”

In trading lingo, a “coil” or “squeeze” is when price has been chopping around in a very **narrow range** (i.e. low volatility) for a stretch of time—think of it like compressing or “coiling” a spring.  The idea is that once volatility is depressed, you often get a **strong breakout** as the spring “uncoils.”

* In the **full** script we computed this by looking at the **high–low range** each day, averaging it over a short window, and then checking that average was below some historical percentile.
* In the **simple** “coil→zoom” version I gave you, we didn’t explicitly measure volatility—you simply define a **consolidation window** (`--cons-days`) during which you assume the market was coiling.

If you really want a true “low-volatility” filter, you’d need to re-introduce something like:

```python
df['Range']     = df['High'] - df['Low']
df['Avg_Range'] = df['Range'].rolling(window=cons_days).mean()
coil_ok        = df['Avg_Range'] < (df['Avg_Range'].rolling(window=long_window).quantile(0.3))
```

—but the minimal script simply treats the last *N* days as your coil, regardless of range.

---

### 2) Only one breakout at 5% / 20 days

That simply means that, in your data set, **only one day** actually closed at least **5% above the previous 20-day high**.  If you bump the threshold down (say to `--zoom-pct 0.03` for 3%) or shorten the window (e.g. `--cons-days 10`), you’ll generally see more signals:

```bash
python simple_zoom_breakout.py --csv scrip.csv --cons-days 20 --zoom-pct 0.03
```

---

### 3) Why “Close” and “Max\_Close” look like percentages

That’s purely a formatting choice: in the example I printed

```python
print(zoomed[['Close','Max_Close','Pct_Above']].to_string(
    float_format='{:.2%}'.format
))
```

Using `'{:.2%}'` tells Python to **multiply each number by 100** and append a “%” sign.  So:

* A raw Close of **6275.35** becomes **627535.00%**.
* If you want to see the actual price numbers instead, switch to something like `'{:,.2f}'`:

  ```python
  print(zoomed[['Close','Max_Close','Pct_Above']].to_string(
      float_format='{:,.2f}'.format
  ))
  ```

---

#### TL;DR

1. **Coiling** = low volatility → spring.  Simple script just uses “last N days” as a proxy.
2. **One signal** means only one day met your 5%/20d rule.  Loosen it for more.
3. **“%” formatting** came from using `'{:.2%}'`; change your `float_format` to see raw prices.
