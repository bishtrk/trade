Consolidation + Breakout

Measure daily high–low ranges and compute a short-term average.

Define a “squeeze” when that average falls below the percentile of its longer-term history.

Compute a rolling resistance line (highest high over price-lookback days).

Flag only those closes that both (a) break that resistance and (b) occur during a low-volatility squeeze.

Pros: Filters out false breakouts, only shows moves emerging from real range-compressions.

Cons: More parameters to tune and slightly slower to run.

---
Close > rolling high over last N days and that day falls inside a measured low-volatility squeeze (range-based)	

A more refined “spring out of a true coil” filter. Use when you want to avoid random spikes and only trade after a genuine volatility compression. Great for medium-frequency swing trades.	

A stock whose daily ranges have been in the bottom 30% of their 50-day history, then closes above its 20-day high.



---

## 1. Load & clean your data

* **`load_data`** reads your CSV, parses the “Date” column into a proper DateTime index, and renames the price columns to simple names (`High`, `Low`, `Close`).

---

## 2. Find your resistance breakout

* **Resistance**: for each day, look back *N* days (e.g. 20), take the highest **High** in that window **excluding today**, and call that your “Resistance” level.
* **Price\_Breakout**: flag any day where **Close > Resistance**.

  ```python
  Resistance_t = max(High_{t-1}, High_{t-2}, …, High_{t-N})
  Price_Breakout_t = (Close_t > Resistance_t)
  ```

---

## 3. Detect periods of “squeeze” (consolidation)

* **Daily Range** = High – Low.
* **Avg\_Range** = the average of yesterday’s ranges over a short window (e.g. 10 days).
* **Cons\_Threshold** = the 30th-percentile of those average ranges over a longer window (e.g. 50 days).
* **Consolidating** = when your recent Avg\_Range is below that historical threshold—i.e., price action is unusually tight (“squeezed”).

  ```python
  Avg_Range_t  = mean(Range_{t-1} … Range_{t-10})
  Threshold_t  = 30% quantile of Avg_Range_{t-1} … Avg_Range_{t-50}
  Consolidating_t = (Avg_Range_t < Threshold_t)
  ```

---

## 4. Combine into “breakout after consolidation”

* **Breakout\_Consol** = `Price_Breakout` **AND** `Consolidating`.
* You’ll only mark signals on days where price breaks its recent highs **while** it has been in a tight consolidation.

---

## 5. Print your signals

* Any days that satisfy both conditions get printed as a little table (`Close`, `Resistance`, `Avg_Range`, `Cons_Threshold`).

---

## 6. Plot it all together

* **Price** (`Close`) as a solid line, with the **Resistance** as a dashed line.
* **Shaded grey zones** wherever you’re in “consolidation.”
* **Green triangles** on the exact days that fired your “breakout after consolidation” signal.
* **Volume bars** on a second y-axis:

  * All days in light alpha
  * Signal days overlaid in solid color

---

### Why each piece matters

* **Resistance breakout** spots fresh momentum, when price finally exceeds its recent ceiling.
* **Consolidation filter** avoids false breakouts by waiting for a tight range—true thrust often follows a squeeze.
* **Volume overlay** gives context: higher volume on your signal days tends to make them more reliable.

Taken together, this simple screener can help you spot potentially actionable momentum setups where price “coils” (consolidates) and then “springs” (breaks out) with real conviction.


---

1. **Resistance**: Highest High over the last `price_lookback` days, excluding today.
2. **Avg\_Range**: The mean daily range (`High–Low`) over the prior `cons_window` days—shifted to avoid lookahead.
3. **Cons\_Threshold**: The `percentile` (e.g. 0.3 for 30th percentile) of `Avg_Range` over the last `long_window` days—also lagged.
4. **Consolidating**: Flags bars where `Avg_Range` is below that threshold (a “squeeze”).
5. **Breakout\_Consol**: True only if we have both a **Price\_Breakout** (close > resistance) **and** a **Consolidating** condition.

Run with your own `--cons-window`, `--long-window`, and `--percentile` to tune how tight a consolidation must be.
