Yes, absolutely — the `generate_signals(df, fast=20, slow=50)` function is designed to allow easy switching between different SMA periods. You can change the `fast` and `slow` parameters to any values you want.

---

### ✅ Example

To use a **10-day** fast SMA and a **30-day** slow SMA:

```python
df = generate_signals(df, fast=10, slow=30)
```

---

### ✅ Modify in `main()`:

In your script’s `main()` function:

```python
def main():
    df = load_data()
    df = generate_signals(df, fast=10, slow=30)  # <== update here
    equity_df, trades_df = backtest_with_stats(df, initial_capital=100_000)
    summarize_and_plot(equity_df, trades_df)
```

---

### 🔁 You could even turn it into a loop:

To backtest multiple combinations:

```python
for fast, slow in [(10, 30), (20, 50), (50, 200)]:
    print(f"\nTesting SMA crossover with fast={fast}, slow={slow}")
    df = load_data()
    df = generate_signals(df, fast=fast, slow=slow)
    equity_df, trades_df = backtest_with_stats(df)
    summarize_and_plot(equity_df, trades_df)
```

Let me know if you want to automate testing multiple combinations or optimize the crossover pairs using grid search.
