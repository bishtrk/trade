#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def load_data(path):
    """Load CSV, parse dates, strip commas, rename and convert columns."""
    df = pd.read_csv(path, thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'High Price':            'High',
        'Low Price':             'Low',
        'Close Price':           'Close',
        'Total Traded Quantity': 'Volume'
    }, inplace=True)
    # ensure numeric types
    for col in ['High','Low','Close','Volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    # drop duplicate dates if any
    df = df[~df.index.duplicated(keep='first')]
    return df

def detect_price_breakouts(df, lookback):
    """Compute resistance line, detect price breakouts, and avg volume."""
    df = df.copy()
    # resistance = max high over prior lookback days
    df['Resistance'] = (
        df['High']
          .shift(1)
          .rolling(window=lookback, min_periods=1)
          .max()
    )
    # raw breakout flag
    df['Breakout'] = df['Close'] > df['Resistance']
    # lagged average volume over same lookback
    df['Avg_Volume'] = (
        df['Volume']
          .shift(1)
          .rolling(window=lookback, min_periods=1)
          .mean()
    )
    return df

def check_follow_through(df, dt, follow_days, pct):
    """Check candle-top close and no fallback over follow_days."""
    res   = float(df.at[dt, 'Resistance'])
    high  = float(df.at[dt, 'High'])
    low   = float(df.at[dt, 'Low'])
    close = float(df.at[dt, 'Close'])
    # 1) did it close in the upper pct of its own bar?
    if close < low + pct * (high - low):
        return False
    # 2) no fallback below resistance in next follow_days
    window = df.loc[dt:].iloc[1:follow_days+1]
    return (not window.empty) and (window['Close'] > res).all()

def backtest(df, bo_dates, follow_days, pct, back_days):
    """
    Returns (total_breakouts, follow_through_dates, sustain_dates).
    """
    ft_dates = []
    sustain_dates = []
    for dt in bo_dates:
        if check_follow_through(df, dt, follow_days, pct):
            ft_dates.append(dt)
        # check N-day later sustain
        b_close = float(df.at[dt, 'Close'])
        future = df.loc[dt:].iloc[back_days:back_days+1]
        if not future.empty and float(future['Close'].iat[0]) > b_close:
            sustain_dates.append(dt)
    return len(bo_dates), ft_dates, sustain_dates

def plot_price_volume(df, bo_dates, ft_dates):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    # price & resistance
    ax1.plot(df.index, df['Close'], label='Close', lw=1.2)
    ax1.plot(df.index, df['Resistance'], '--', color='orange', label='Resistance')
    # markers
    ax1.scatter(bo_dates, [df.at[d,'Close'] for d in bo_dates],
                marker='o', color='red', label='Breakout', zorder=5)
    ax1.scatter(ft_dates, [df.at[d,'Close'] for d in ft_dates],
                marker='^', color='green', label='Follow-through', zorder=6)
    ax1.set_ylabel('Price')
    ax1.legend(loc='upper left')
    # volume bars
    ax2 = ax1.twinx()
    ax2.bar(df.index, df['Volume'], width=1, alpha=0.3)
    ax2.set_ylabel('Volume')
    plt.title('Price & Volume with Breakouts and Follow-through')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="Breakout + Follow-through + Table + Chart")
    p.add_argument('--csv',         default='scrip.csv', help="Path to CSV")
    p.add_argument('--lookback',    type=int,   default=20,   help="Resistance/vol lookback days")
    p.add_argument('--follow-days', type=int,   default=3,    help="Days to check no-fallback")
    p.add_argument('--pct',         type=float, default=0.6,  help="Close must be in top pct of candle")
    p.add_argument('--back-days',   type=int,   default=10,   help="Days forward to test sustain")
    args = p.parse_args()

    # load, detect breakouts & compute avg volume
    df = load_data(args.csv)
    df = detect_price_breakouts(df, args.lookback)
    bo_dates = df.index[df['Breakout']].tolist()
    if not bo_dates:
        print("No breakouts detected.")
        exit()

    # run backtest
    total, ft_dates, sustain_dates = backtest(
        df, bo_dates, args.follow_days, args.pct, args.back_days
    )

    # summary
    print(f"Total breakouts:       {total}")
    print(f"Follow-through count:  {len(ft_dates)}")
    print(f"Sustained count:       {len(sustain_dates)}")
    print(f"Follow-through rate:   {len(ft_dates)/total*100:.1f}%")
    print(f"Sustain rate:          {len(sustain_dates)/total*100:.1f}%\n")

    # detailed table
    rows = []
    for dt in bo_dates:
        vol     = df.at[dt, 'Volume']
        avg_vol = df.at[dt, 'Avg_Volume']
        rows.append({
            'Date':       dt.strftime('%Y-%m-%d'),
            'Close':      df.at[dt, 'Close'],
            'Resistance': df.at[dt, 'Resistance'],
            'Volume':     vol,
            'Avg_Volume': avg_vol,
            'HighVol':    vol > avg_vol if avg_vol>0 else False,
            'FollowThru': dt in ft_dates,
            f'Sustain@{args.back_days}d': dt in sustain_dates
        })
    table = pd.DataFrame(rows).set_index('Date')
    print(table.to_string(
        float_format='{:,.2f}'.format,
        columns=['Close','Resistance','Volume','Avg_Volume','HighVol','FollowThru',f'Sustain@{args.back_days}d']
    ))

    # plot chart
    plot_price_volume(df, bo_dates, ft_dates)

#python breakout_followthrough_backtest.py --csv scrip.csv  --lookback 20 --follow-days 3 --pct 0.6 --back-days 10
