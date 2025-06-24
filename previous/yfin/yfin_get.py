import yfinance as yf
import pandas as pd

# Define the ticker symbol for Infosys on NSE
ticker_symbol = "INFY.NS"

# Fetch the stock data
stock = yf.Ticker(ticker_symbol)

# Function to save data to CSV
def save_to_csv(data, filename):
    if isinstance(data, (pd.DataFrame, pd.Series)):
        data.to_csv(filename)
        print(f"Saved {filename}")
    else:
        print(f"Skipped {filename} (not a DataFrame or Series)")

income_stmt=stock.income_stmt
save_to_csv(income_stmt, "income_stmt.csv")

# 1. Historical Market Data
historical_data = stock.history(period="max")  # Options: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
save_to_csv(historical_data, "historical_data.csv")

# 2. Dividends
dividends = stock.dividends
save_to_csv(dividends, "dividends.csv")

# 3. Stock Splits
splits = stock.splits
save_to_csv(splits, "splits.csv")

# 4. Financials (Income Statement, Balance Sheet, Cash Flow)
financials = stock.financials  # Annual financials
save_to_csv(financials, "financials.csv")

quarterly_financials = stock.quarterly_financials  # Quarterly financials
save_to_csv(quarterly_financials, "quarterly_financials.csv")

# 5. Balance Sheet
balance_sheet = stock.balance_sheet  # Annual balance sheet
save_to_csv(balance_sheet, "balance_sheet.csv")

quarterly_balance_sheet = stock.quarterly_balance_sheet  # Quarterly balance sheet
save_to_csv(quarterly_balance_sheet, "quarterly_balance_sheet.csv")

# 6. Cash Flow
cash_flow = stock.cashflow  # Annual cash flow
save_to_csv(cash_flow, "cash_flow.csv")

quarterly_cash_flow = stock.quarterly_cashflow  # Quarterly cash flow
save_to_csv(quarterly_cash_flow, "quarterly_cash_flow.csv")

# 7. Earnings (Income Statement)
earnings = stock.earnings  # Annual earnings
save_to_csv(earnings, "earnings.csv")

quarterly_earnings = stock.quarterly_earnings  # Quarterly earnings
save_to_csv(quarterly_earnings, "quarterly_earnings.csv")

# 8. Sustainability/ESG Scores
sustainability = stock.sustainability
save_to_csv(sustainability, "sustainability.csv")

# 9. Recommendations (Analyst Recommendations)
recommendations = stock.recommendations
save_to_csv(recommendations, "recommendations.csv")

# 10. Options (Expiration Dates and Option Chains)
options = stock.options  # List of expiration dates
if options:
    with open("options_expiration_dates.txt", "w") as f:
        f.write("\n".join(options))
    print("Saved options_expiration_dates.txt")

    # Fetch option chains for the first expiration date
    opt_chain = stock.option_chain(options[0])
    save_to_csv(opt_chain.calls, "options_calls.csv")
    save_to_csv(opt_chain.puts, "options_puts.csv")
else:
    print("No options data available.")

# 11. Institutional Holders
institutional_holders = stock.institutional_holders
save_to_csv(institutional_holders, "institutional_holders.csv")

# 12. Major Holders
major_holders = stock.major_holders
save_to_csv(major_holders, "major_holders.csv")

# 13. News
news = stock.news
if news:
    import json
    with open("news.json", "w") as f:
        json.dump(news, f, indent=4)
    print("Saved news.json")
else:
    print("No news data available.")

# 14. Info (Fundamental Data)
info = stock.info
if info:
    with open("info.json", "w") as f:
        json.dump(info, f, indent=4)
    print("Saved info.json")
else:
    print("No info data available.")