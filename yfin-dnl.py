import yfinance as yf
import pandas as pd

# ===== USER CONFIGURATION =====
# Edit these variables as needed
TICKER_SYMBOL = "MSFT"  # NSE stock symbol without '.NS' suffix
PERIOD = "3mo"               # Data period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
INTERVAL = "1wk"             # Data interval: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
OUTPUT_FILE = "ohlcv_data.csv"  # Output CSV filename
# =============================

def download_nse_ohlcv_to_csv():
    """
    Download OHLCV data for an NSE stock and save to CSV using the predefined parameters.
    """
    # Add '.NS' suffix for NSE stocks in yfinance
    full_ticker = f"{TICKER_SYMBOL}"
    
    try:
        # Download data
        print(f"Downloading {PERIOD} of {INTERVAL} data for {TICKER_SYMBOL}...")
        stock = yf.Ticker(full_ticker)
        df = stock.history(period=PERIOD)
        
        if df.empty:
            print(f"No data found for {TICKER_SYMBOL}. Please check the ticker symbol.")
            return False
        
        # Rename columns to match standard OHLCV format
        df = df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Save to CSV
        df.to_csv(OUTPUT_FILE)
        print(f"Successfully downloaded data for {TICKER_SYMBOL}")
        print(f"Saved to: {OUTPUT_FILE}")
        print(f"Data shape: {df.shape}")
        return True
    
    except Exception as e:
        print(f"Error downloading data: {e}")
        return False

if __name__ == "__main__":
    download_nse_ohlcv_to_csv()