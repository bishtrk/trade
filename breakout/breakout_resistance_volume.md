To combine **Breakout Above Previous Resistance** with **Volume Confirmation**, you simply require **both** conditions to be true on the same day:

1. **Price Breakout**:

   * Today’s **Close** > max High over the prior *P* days (shifted by one to exclude today).

2. **Volume Confirmation**:

   * Today’s **Volume** > *V* × (average Volume over the prior *Vₗ* days, shifted by one).

Only days where **both** (1) and (2) are true become your **validated breakout** signals.

---

### Combined Logic

```python
# 1. Resistance breakout:
df['Resistance']    = df['High'].shift(1).rolling(P).max()
df['Price_Breakout'] = df['Close'] > df['Resistance']

# 2. Volume filter:
df['Avg_Volume']    = df['Volume'].shift(1).rolling(Vₗ).mean()
df['Volume_Confirm'] = df['Volume'] > V * df['Avg_Volume']

# 3. Valid breakout:
df['Validated_Breakout'] = df['Price_Breakout'] & df['Volume_Confirm']
```

* **P** = lookback for resistance (e.g. 20)
* **Vₗ** = lookback for average volume (e.g. 20)
* **V** = volume‐multiple (e.g. 1.5)

---

### Full Script: `breakout_resistance_volume.py`

Save alongside `scrip.csv`, then:

```bash
pip install pandas
python breakout_resistance_volume.py --price-lookback 20 --vol-lookback 20 --vol-mult 1.5
```

```python
#!/usr/bin/env python3
import argparse
import pandas as pd

def load_data(path):
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'High Price':            'High',
        'Close Price':           'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)
    return df

def detect_valid_breakouts(df, price_lookback, vol_lookback, vol_mult):
    # 1. Price breakout above prior resistance
    df['Resistance']     = df['High'].shift(1).rolling(price_lookback, min_periods=1).max()
    df['Price_Breakout'] = df['Close'] > df['Resistance']

    # 2. Volume confirmation
    df['Avg_Volume']     = df['Volume'].shift(1).rolling(vol_lookback, min_periods=1).mean()
    df['Volume_Confirm'] = df['Volume'] > vol_mult * df['Avg_Volume']

    # 3. Validated breakout (both conditions)
    df['Validated_Breakout'] = df['Price_Breakout'] & df['Volume_Confirm']
    return df

def main():
    parser = argparse.ArgumentParser(description="Detect breakouts above resistance with volume confirmation")
    parser.add_argument('--csv',            default='scrip.csv', help="Path to scrip.csv")
    parser.add_argument('--price-lookback', type=int,   default=20, help="Days for resistance lookback")
    parser.add_argument('--vol-lookback',   type=int,   default=20, help="Days for average volume")
    parser.add_argument('--vol-mult',       type=float, default=1.5, help="Volume multiple for confirmation")
    args = parser.parse_args()

    df = load_data(args.csv)
    df = detect_valid_breakouts(df, args.price_lookback, args.vol_lookback, args.vol_mult)

    signals = df[df['Validated_Breakout']]
    if signals.empty:
        print("No validated breakouts found.")
    else:
        pd.set_option('display.float_format', '{:,.2f}'.format)
        print(f"Validated Breakouts (Price lookback={args.price_lookback}d, Vol lookback={args.vol_lookback}d, Vol mult={args.vol_mult}):\n")
        print(signals[['Close','Resistance','Volume','Avg_Volume']].to_string())

if __name__ == '__main__':
    main()
```

**Usage Example:**

```bash
python breakout_resistance_volume.py \
  --price-lookback 20 \
  --vol-lookback 20 \
  --vol-mult 1.5
```

This will list all days where TCS’s close pierced the 20-day high **and** volume exceeded 1.5× its 20-day average—your strongest, volume-backed breakouts.
