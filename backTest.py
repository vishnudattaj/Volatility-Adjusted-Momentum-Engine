import pandas as pd
from tqdm import tqdm


def buyStocks(investments, master, holdings, date, stock_price, yesterday=None, networthScale=70000):
    prices = master.loc[date, investments]
    if yesterday is not None:
        amount = stock_price.loc[yesterday, investments]
    else:
        amount = stock_price.loc[date, investments]

    scaled_amount = amount * (networthScale / 70000)

    share_counts = scaled_amount // prices
    holdings.update(share_counts.to_dict())

    return (scaled_amount % prices).sum(), scaled_amount.sum()

def sellStocks(investments, open_prices, holdings, date):
    if not investments:
        return 0

    prices = open_prices.loc[date, investments]
    if isinstance(prices, float):
        prices = pd.Series({investments: prices})

    total_cash_gained = 0

    for ticker in investments:
        if ticker in holdings:
            qty = holdings[ticker]
            price = prices[ticker]

            total_cash_gained += qty * price
            del holdings[ticker]

    return total_cash_gained

def sellSignals(investments, master, date):
    signals = master.loc[date, investments]
    negative_signals = signals[signals < 0]

    return negative_signals.index.tolist()

current_cash = 70000
master_df = pd.read_parquet("masterData.parquet")
topStocks = pd.read_parquet("baseline_stats.parquet")
topStocks['price-sum'] = topStocks['stock-price'].cumsum()
baseline_top = topStocks[topStocks['price-sum'] <= current_cash]

dates = master_df.index
holdings = {}
setBuy = False
setSell = False
networth = []
cashHistory = []

open_prices = master_df['Open'].ffill()
close_prices = master_df['Close'].ffill()
signals = master_df['risk-adj-signal'].fillna(0)
volume = master_df['daily-volume'].ffill()
stock_price = master_df['stock-price'].ffill()
trend200 = master_df["trend200"].ffill()
combined = pd.concat([signals, stock_price, trend200], axis=1, keys=['Signal', 'Price', 'trend200'])

for i in tqdm(range(len(dates)), desc="Backtesting Strategy"):
    index = dates[i]
    yesterday = dates[i-1]

    if i == 0:
        investments = baseline_top["Ticker"].tolist()
        leftover_change, totalAmount = buyStocks(investments, open_prices, holdings, index, stock_price)
        current_cash = current_cash - totalAmount + leftover_change
        networth.append(totalAmount)

    else:
        if setBuy:
            leftover_change, totalAmount = buyStocks(investmentList, open_prices, holdings, index, stock_price, yesterday, networthScale=current_cash + market_value)
            current_cash = current_cash + leftover_change - totalAmount
            setBuy = False

        if setSell:
            max_portfolio_size = 100
            current_count = len(holdings)
            slots_available = max_portfolio_size - current_count

            current_cash += sellStocks(sellList, open_prices, holdings, index)

            day_data = combined.loc[index].unstack(level=0)

            day_data['Volume'] = volume.loc[index]
            day_data['Price_Actual'] = close_prices.loc[index]

            filtered_candidates = day_data[
                (day_data['Price_Actual'] > 5) &
                (day_data['Volume'] > 1500000) &
                (day_data['trend200'] > 0)
                ].copy()

            filtered_candidates = filtered_candidates.drop(labels=holdings.keys(), errors='ignore')

            filtered_candidates = filtered_candidates.sort_values(by='Signal', ascending=False)
            filtered_candidates['price-sum'] = (filtered_candidates['Price'] * ((current_cash + market_value) / 70000)).cumsum()

            stocks_we_can_afford = filtered_candidates[filtered_candidates['price-sum'] < current_cash]

            num_to_pick = min(len(stocks_we_can_afford), slots_available)
            if num_to_pick > 0:
                top_picks = stocks_we_can_afford.head(num_to_pick)
                investmentList = top_picks.index.tolist()
                setBuy = True

            setSell = False

        sellList = sellSignals(list(holdings.keys()), signals, index)
        if sellList:
            setSell = True

        current_tickers = list(holdings.keys())
        if current_tickers:
            market_value = sum(holdings[t] * close_prices.at[index, t] for t in holdings)
        else:
            market_value = 0

        networth.append(current_cash + market_value)
        cashHistory.append(current_cash)
    holdings = {ticker: qty for ticker, qty in holdings.items() if qty > 0}

results_df = pd.DataFrame({
    'Date': dates,
    'Net_Worth': networth,
})

cash = pd.DataFrame(cashHistory)

results_df.to_csv("backtest_history.csv", index=False)
cash.to_csv("cash.csv", index=False)
