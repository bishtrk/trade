Here’s a structured breakdown and analysis of the Classic Turtle Trading System:

---

## 1. Strategy Overview

* **Origins:** Developed in the early 1980s by Richard Dennis and William Eckhardt, the Turtles proved that a clear, mechanical rule set could be taught to novices and yield strong results.
* **Core Signals:**

  * **Entry:** Buy when price breaks **above** the 20-day high (long); sell short when price breaks **below** the 20-day low.
  * **Exit:** Close longs when price breaks **below** the 10-day low; cover shorts when price breaks **above** the 10-day high.

---

## 2. Position Sizing with ATR

* **Volatility Adjustment:**

  * Compute the Average True Range (ATR) over, say, 20 days.
  * Define a “volatility unit” (V = ATR).
  * Risk a fixed percentage of account equity (typically 1–2%) per unit:

    $$
      \text{UnitSize} = \frac{\text{Equity} \times \text{Risk \%}}{\text{ATR} \times \text{DollarValuePerPoint}}
    $$
* **Benefit:** Larger positions in quiet markets (low ATR), smaller in choppy/high-volatility markets.

---

## 3. Pyramiding (Adding to Winners)

* **Pyramid Trigger:** After the initial entry, add another “unit” when price moves in your favor by 0.5 × ATR.
* **Cap:** Typically up to 4 units maximum (initial + 3 adds).
* **Rationale:** Let profits run and compound gains during strong trends, while still cutting losses early on the first unit’s stop.

---

## 4. Risk Management & Stops

* **Stop-Loss:** Place initial stop at 2 × ATR below entry (for longs), above entry (for shorts).
* **Risk per Trade:** By risking only 1–2% of equity per unit, even a string of losers won’t devastate your account.
* **Equity Curve Smoothing:** Volatility-based sizing and systematic stops help control drawdowns.

---

## 5. Strengths & Weaknesses

| Strengths                                                                                | Weaknesses                                                                                 |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 1. **Mechanical & Objective:** Easy to backtest and remove emotional bias.               | 1. **Whipsaws in Ranging Markets:** Frequent false breakouts when no clear trend exists.   |
| 2. **Volatility-Adjusted Sizing:** Naturally scales with market conditions.              | 2. **Drawdown Depth:** Can suffer long, deep drawdowns during trendless periods.           |
| 3. **Pyramiding Captures Large Moves:** Adds to winners, amplifying gains in big trends. | 3. **Requires Ample Capital:** Worst-case drawdowns demand sufficient equity to survive.   |
| 4. **Proven Track Record:** Historically robust across commodities, futures, and FX.     | 4. **Transaction Costs:** Multiple entries/exits and wide stops can rack up slippage/fees. |

---

## 6. Implementation & Backtesting Tips

1. **Data Preparation:** Calculate rolling 20-day highs/lows and 10-day lows/highs, plus 20-day ATR.
2. **Trade Logic:**

   * On a 20-day breakout, enter with one ATR-sized unit and set a 2×ATR stop.
   * On each +0.5×ATR move, pyramid another unit (up to max).
   * Exit all units on the 10-day counter-break.
3. **Risk Controls:** Cap max drawdown per system, enforce daily stop-loss limits.
4. **Performance Metrics:** Track CAGR, max drawdown, Sharpe ratio, percent profitable, average win/loss.
5. **Walk-Forward Testing:** Validate parameter robustness (e.g., 15–25 day channel, 8–12 day exit).

---

### Conclusion

The Turtle system exemplifies disciplined trend following: it hunts strong, sustained moves while cutting losers quickly. Its volatility-based sizing and pyramiding rules let winners run, but practitioners must be prepared for extended whipsaws and allocate sufficient capital to weather drawdowns. Proper backtesting—incorporating realistic slippage, commission, and walk-forward validation—is essential before live deployment.


--- Variations:

## 1. Entry/Exit Signal Variations

| Component         | Classic                       | Variations                                                                                                                                                                                                                                              |
| ----------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Entry**         | 20-day high/low               | • **Alternate look-backs**: 10/30/55 days<br>• **Keltner Breakout**: ATR-based channel instead of pure Donchian<br>• **Volatility-scaled channel**: N×ATR above/below moving average<br>• **Multi-timeframe**: daily breakout confirmed on 4-hour chart |
| **Exit (Stop)**   | 10-day low/high               | • **Fixed ATR stop**: e.g. 2×ATR from entry<br>• **Moving-average cross**: e.g. 5-day EMA crossing below 20-day EMA<br>• **Time stop**: exit after N days no matter what<br>• **Volatility stop**: price falling below Bollinger Band midline           |
| **Exit (Profit)** | Pyramid exits + counter-break | • **Parabolic SAR** exit<br>• **Momentum reversion**: ROC turning negative<br>• **Partial profit taking**: scale out at defined R-multiples (e.g. +2×ATR)                                                                                               |

---

## 2. Position Sizing & Money Management

* **Volatility sizing (Classic ATR-unit)**
  − Risk X% of equity per ATR unit
* **Fixed-fractional**
  − Risk a constant % per trade, independent of ATR
* **Kelly or growth-optimal**
  − Size based on expected edge & variance
* **Equal-dollar or equal-weight**
  − Each position represents same notional amount
* **Risk parity across asset classes**
  − Allocate ATR units so each instrument contributes equally to portfolio risk

---

## 3. Pyramiding Schemes

* **Classic Turtle:** add 1 ATR unit every +0.5×ATR move, up to 4 units
* **Scaled pyramiding:** add when price moves +1×ATR, fewer total adds
* **Signal-based add:** only pyramid when a secondary momentum filter (e.g. MACD histogram rising) confirms
* **Time-based pyramiding:** add fixed-size increments every N bars if still above entry

---

## 4. Trend Filters & Hybrid Rules

* **Long-only or short-only in clear regimes**
  − e.g. only take longs when price >200-day MA
* **ADX filter:** only trade when ADX > threshold, to avoid choppy markets
* **Volume filter:** require daily volume > X-day average to confirm breakouts
* **Volatility regime**: use higher look-back or skip trades when ATR is below/above certain band

---

## 5. Portfolio & Execution Variations

* **Multi-instrument rotation**: rank channels across many symbols and trade the top N breakouts
* **Sector/ETF buckets**: apply rules at the sector level (e.g. sector ETF breakouts)
* **Intraday Turtle**: apply 20-bar (e.g. 30-min) channel on intraday bars
* **Execution tweaks**: use limit orders at the channel line, slippage buffers, time-in-force rules

---

## 6. Parameter & Robustness Techniques

* **Walk-forward optimization**: re-optimize lookbacks (20/10 → 25/15 → 15/7) on rolling in-sample windows
* **Ensemble of channels**: combine signals from 10/20/55-day channels (majority vote)
* **Adaptive look-back**: dynamic channel length based on recent volatility or trend strength
* **Machine-learned stops**: replace fixed exits with stops learned from historical drawdown patterns

---

### In practice you might…

1. **Test** several entry/exit pairs (e.g. 55/20, 20/10, 10/5) and pick the most robust.
2. **Add** a long-only filter in bull regimes (200-day MA) and short-only in bear regimes.
3. **Swap** Donchian channels for Keltner channels when ATR spikes.
4. **Combine** with simple momentum (e.g. require N-day ROC > 0 to permit entries).
5. **Optimize** the pyramid trigger distance (0.5×ATR vs 1×ATR) to balance whipsaws vs capture.

Each tweak trades off responsiveness versus noise-immunity, so you can dial it to your preferred risk profile and instrument.


--
Implements the Turtle breakouts:

Long entry when today’s close > highest high of the prior 20 days

Short entry when today’s close < lowest low of the prior 20 days

Long exit when today’s close < lowest low of the prior 10 days

Short exit when today’s close > highest high of the prior 10 days

---
Donchian Channels

Highest(self.data.high, period=20) and Lowest(self.data.low, period=20) compute 20-day channels.

We compare today’s close to the previous bar’s channel (self.high20[-1]) so we don’t “peek.”

Entries & Exits

Long: buy 1 unit on a 20-day high breakout; exit on a 10-day low breakout.

Short: symmetrical rules using 20-day lows & 10-day highs.

Trade Logging

notify_order inspects each completed buy()/sell() to determine whether it’s an entry or an exit, then logs side, dates, prices, PnL and PnL%.

We compute hold_days as the difference between exit & entry dates.

No pyramiding

We only ever hold one contract/unit at a time—no additional adds.