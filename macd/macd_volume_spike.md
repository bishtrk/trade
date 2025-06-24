**How to Use This Script**

1. **Save** the code as `macd_volume_spike.py` in the same folder as your `scrip.csv`.

2. **Install dependencies**:

   ```bash
   pip install pandas numpy
   ```

3. **Run** in your terminal (not inside Jupyter) to see all MACD bullish crossovers confirmed by a volume spike:

   ```bash
   python macd_volume_spike.py --vol-window 20 --vol-mult 1.5
   ```

* `--vol-window`: number of days for average volume (default: 20)
* `--vol-mult`: multiplier of that average to qualify as a spike (default: 1.5×)

The script will print dates where a **MACD crossover** coincided with **today’s volume > 1.5× the 20-day average**, along with the Close price, Volume, AvgVol, MACD, and Signal values.
