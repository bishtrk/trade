ADX filter: only trade when ADX > threshold, to avoid choppy markets
Volume filter: require daily volume > X-day average to confirm breakouts
Moving-average cross: e.g. 5-day EMA crossing below 20-day EMA

Entry: Buy when price breaks above the 20-day high (long); 
exit: Close longs when price breaks below the 10-day low




===
The **Turtle Trading Strategy** is one of the most famous **trend-following systems** in trading history. Developed by **Richard Dennis and William Eckhardt** in the 1980s, it was part of an experiment to prove that successful trading could be taught—even to complete beginners (dubbed the "Turtles").  

---

### **Core Principles of Turtle Trading**  
The strategy is built on **breakouts, volatility-based position sizing, and strict risk management**.  

#### **1. Entry Rules**  
- **Long Entry**: Buy when price breaks above the **highest high of the last 20 days**.  
- **Short Entry**: Sell short when price breaks below the **lowest low of the last 20 days**.  
- **Alternative Entry (for aggressive traders)**:  
  - 55-day breakout for stronger trends (fewer trades, but higher reliability).  

#### **2. Position Sizing (Risk Management)**  
- **Volatility Adjustment**: Use the **Average True Range (ATR)** to determine position size.  
  - Higher ATR = smaller position (to control risk).  
  - Lower ATR = larger position.  
- **Fixed Risk per Trade**: Typically **1-2% of capital risked per trade**.  

#### **3. Exit Rules**  
- **Long Exit**: Sell when price drops below the **lowest low of the last 10 days**.  
- **Short Exit**: Cover when price rises above the **highest high of the last 10 days**.  
- **Stop-Loss**: Some versions use **2x ATR** as a trailing stop.  

#### **4. Pyramiding (Adding to Winning Trades)**  
- **Add to positions** in fixed increments (e.g., every **0.5x ATR move** in favor).  
- **Maximum 4 units per trade** (to avoid overexposure).  

---

### **Why Did It Work?**  
- **Captures Big Trends**: Designed to ride strong momentum moves (e.g., commodities, forex, stocks).  
- **Volatility-Based Sizing**: Adjusts position size dynamically, reducing risk in choppy markets.  
- **Disciplined Exit Rules**: Locks in profits while cutting losses quickly.  

---

### **Performance & Criticisms**  
✅ **Pros**:  
- **Massive gains in trending markets** (e.g., 100%+ returns in strong bull/bear markets).  
- **Systematic, rule-based** (removes emotional trading).  

❌ **Cons**:  
- **High Drawdowns** (30-50% in range-bound markets).  
- **Whipsaws** (many false breakouts in choppy conditions).  
- **Requires Discipline** (many traders abandon it during losing streaks).  

---

### **Modern Adaptations**  
Many traders modify the classic Turtle rules with:  
- **Trend Filters** (e.g., only trade breakouts when price is above a 200-day MA).  
- **Momentum Confirmation** (e.g., RSI or MACD to avoid weak breakouts).  
- **Multi-Asset Diversification** (reduces reliance on a single market).  

---

### **Key Takeaway**  
The Turtle Trading Strategy is a **pure trend-following system** that thrives in **strongly trending markets** but struggles in sideways conditions. Its success depends on **strict discipline, risk management, and patience**—qualities that made the original Turtles legendary traders.  

Would you like a **Python backtest example** or more details on how to adapt it for modern markets?