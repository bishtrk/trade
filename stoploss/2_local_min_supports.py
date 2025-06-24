#!/usr/bin/env python3
import pandas as pd
import numpy as np

def compute_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_prev = (df['High'] - df['Close'].shift(1)).abs()
    low_prev  = (df['Low']  - df['Close'].shift(1)).abs()
    tr = pd.concat([high_low, high_prev, low_prev], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def find_breakouts(df, lookback=20):
    rolling_max = df['High'].shift(1).rolling(window=lookback).max()
    return df['Close'] > rolling_max

def find_local_minima(series, order=2):
    """Return a boolean series marking local minima over ±order bars."""
    is_min = pd.Series(True, index=series.index)
    for i in range(1, order+1):
        is_min &= series < series.shift(i)
        is_min &= series < series.shift(-i)
    return is_min

def cluster_minima(values, tol_abs):
    """Cluster sorted values: groups where diff from first ≤ tol_abs."""
    if len(values) == 0:
        return []
    sorted_vals = sorted(values)
    clusters = []
    current = [sorted_vals[0]]
    for v in sorted_vals[1:]:
        if v - current[0] <= tol_abs:
            current.append(v)
        else:
            clusters.append(current)
            current = [v]
    clusters.append(current)
    return clusters

def compute_stop_levels_localmin(
    df,
    breakout_lookback=20,
    support_window=10,
    local_order=2,
    tol_pct=0.005,
    buffer_pct=0.005,
    atr_period=14
):
    df = df.copy()
    df['ATR'] = compute_atr(df, period=atr_period)
    df['Breakout'] = find_breakouts(df, lookback=breakout_lookback)

    records = []
    for date in df.index[df['Breakout']]:
        close = df.at[date, 'Close']
        atr   = df.at[date, 'ATR']
        # window for support search
        window = df.loc[:date].iloc[-support_window-1:-1]
        minima_mask = find_local_minima(window['Low'], order=local_order)
        minima_vals = window.loc[minima_mask, 'Low'].tolist()
        # fallback to simple rolling min if none found
        if not minima_vals:
            support = window['Low'].min()
            zmin = zmax = support
        else:
            tol_abs = tol_pct * close
            clusters = cluster_minima(minima_vals, tol_abs)
            # pick cluster with most members
            best = max(clusters, key=len)
            zmin, zmax = min(best), max(best)
        # buffer = larger of fixed % and ATR
        buffer = max(buffer_pct * close, atr)
        stop = zmin - buffer

        records.append({
            'Date':       date,
            'Close':      close,
            'SupportMin': zmin,
            'SupportMax': zmax,
            'ATR':        atr,
            'Buffer':     buffer,
            'StopPrice':  stop
        })

    return pd.DataFrame(records).set_index('Date')

def main():
    df = pd.read_csv('scrip.csv', thousands=',')
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')
    df.set_index('Date', inplace=True)
    df.rename(columns={
        'Open Price':'Open','High Price':'High',
        'Low Price':'Low','Close Price':'Close'
    }, inplace=True)

    stops = compute_stop_levels_localmin(
        df,
        breakout_lookback=20,
        support_window=10,
        local_order=2,
        tol_pct=0.005,
        buffer_pct=0.005,
        atr_period=14
    )

    if stops.empty:
        print("No breakout signals found.")
    else:
        print("\nLocal-Minima-Based Support & Stop Levels:\n")
        print(stops.to_string(formatters={
            'Close':     '{:.2f}'.format,
            'SupportMin':'{:.2f}'.format,
            'SupportMax':'{:.2f}'.format,
            'ATR':       '{:.2f}'.format,
            'Buffer':    '{:.2f}'.format,
            'StopPrice': '{:.2f}'.format
        }))

if __name__ == '__main__':
    main()
