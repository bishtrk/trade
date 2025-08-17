yes, the ideas is i want to screen stocks which are up certain percentage suddenly. usually there is a reason behind such jumps like a news or something. and i want to capture such breakstocks because they might just start their upwaard journey. at same time i want to reduce risk of false breakouts so that i am not stuck at a high. one way is to see if follow through buying is happening or not. this is why i created this script. but not whether this was correctly captured in the script. Got it ?


----

analyse, plot them on the chart also along with price, volume and SMA. **Yes, you can absolutely automate the process of checking technical indicators like RSI, Stochastics, or MACD** to help decide whether a breakout or follow-through day is “overbought” (and therefore risky to chase).

Here’s how you can do it step by step in Python using the popular library **TA-Lib** or **Pandas TA** (if you can’t install TA-Lib).

---

## **Example: Automated Overbought Check with RSI, Stochastics, and MACD**

**First, install dependencies:**

```bash
pip install pandas_ta yfinance
```

---

### **Sample Python Script**

```python
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# Download historical data
df = yf.download('RELIANCE.NS', period='6mo')

# Calculate RSI (14-day default)
df['RSI'] = ta.rsi(df['Close'], length=14)

# Calculate Stochastics (default settings)
stoch = ta.stoch(df['High'], df['Low'], df['Close'])
df = df.join(stoch)

# Calculate MACD
macd = ta.macd(df['Close'])
df = df.join(macd)

# Define overbought/oversold thresholds
rsi_overbought = 70
k_overbought = 80
d_overbought = 80

# Example: Find recent breakouts (close above 20-day high)
window = 20
df['resistance'] = df['High'].rolling(window=window).max().shift(1)
df['is_breakout'] = df['Close'] > df['resistance']

# Check indicators on breakout days
overbought_breakouts = df[
    (df['is_breakout']) &
    (
        (df['RSI'] > rsi_overbought) |
        (df['STOCHk_14_3_3'] > k_overbought) |
        (df['STOCHd_14_3_3'] > d_overbought)
    )
]

print("Breakouts where at least one indicator is overbought:")
print(overbought_breakouts[['Close', 'RSI', 'STOCHk_14_3_3', 'STOCHd_14_3_3', 'MACD_12_26_9', 'resistance']])
```

---

### **What does this code do?**

* Computes **RSI**, **Stochastic K/D**, and **MACD** for each day.
* Finds days where the **close price breaks out** above the recent 20-day high.
* On those days, **flags as overbought** if RSI > 70, or either stochastic K/D > 80.
* Prints the breakout dates and indicator values.

---

## **How to Use This?**

* **Automate your scan**: Before buying after a breakout or follow-through, run this check to see if indicators are flashing “overbought.”
* **Avoid buying** when all (or most) indicators are overbought, or wait for a pullback.
* **You can expand this** to include EMA distance, MACD crossovers, or other custom filters.

---

### **Summary Table**

| Indicator   | Common Overbought Level | In Code              |
| ----------- | ----------------------- | -------------------- |
| RSI         | > 70                    | `df['RSI'] > 70`     |
| Stoch K / D | > 80                    | `df['STOCHk'] > 80`  |
| MACD        | Above signal line/cross | `df['MACD_12_26_9']` |

---

**In short:**
You can automate overbought checks using indicators in Python to systematically filter out risky entries after a breakout!

Let me know if you want the same with **TA-Lib**, want to add a custom indicator, or want chart plotting!
