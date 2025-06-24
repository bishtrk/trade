python macd_histogram_punch.py --hist-window 10 --hist-mult 0.5

---

Save the above code as `macd_histogram_punch.py` in the same folder as `scrip.csv`. Then install the necessary libraries:

```bash
pip install pandas numpy
```

and run it from your terminal (not inside Jupyter) like so:

```bash
python macd_histogram_punch.py --hist-window 10 --hist-mult 0.5
```

**How It Works:**

1. **Load Data**
   Reads `scrip.csv`, parses dates, and extracts the `Close` column.

2. **MACD & Signal Lines**

   * MACD = EMA(12) − EMA(26)
   * Signal = EMA(9) of MACD

3. **Histogram Calculation**

   * `HIST` = `MACD − Signal`

4. **Bullish Crossover Detection**
   Flags bars where MACD crosses **above** the signal line.

5. **Histogram “Punch” Filter**

   * Calculates a **lagged** rolling average of the absolute histogram over `--hist-window` bars.
   * Requires the current histogram bar to exceed `hist_mult` × this average.

6. **Output**
   Prints all dates where a bullish crossover coincides with a histogram bar at least 50% larger than its recent average—i.e., momentum is clearly accelerating, not just flickering.

Feel free to adjust `--hist-window` (look-back for average) and `--hist-mult` (strength threshold) to suit TCS’s volatility and your style!
