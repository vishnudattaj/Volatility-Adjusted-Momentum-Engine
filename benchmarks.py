import yfinance as yf

START_DATE = "2012-01-03"
END_DATE = "2024-11-04"
INITIAL_CAPITAL = 70000

sp500 = yf.download(
    "^GSPC",
    start=START_DATE,
    end="2024-11-05",
    auto_adjust=True
)

sp500 = sp500[['Close']].copy()

initial_price = sp500['Close'].iloc[0]
shares = INITIAL_CAPITAL / initial_price
sp500['SP500_Net_Worth'] = shares * sp500['Close']

benchmark = sp500[['SP500_Net_Worth']].reset_index()
benchmark.to_csv("sp500_benchmark.csv", index=False)
