import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("backtest_history.csv")
df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d")

sp500 = pd.read_csv("sp500_benchmark.csv")
sp500["Date"] = pd.to_datetime(sp500["Date"])

df = df.merge(sp500, on="Date", how="left")

df["Strategy_norm"] = df["Net_Worth"] / df["Net_Worth"].iloc[0]
df["SP500_norm"] = df["SP500_Net_Worth"] / df["SP500_Net_Worth"].iloc[0]

plt.style.use("dark_background")
plt.figure(figsize=(12, 6))

plt.plot(
    df["Date"],
    df["Strategy_norm"],
    label="Strategy",
    color="#00ffcc",
    linewidth=2
)

plt.plot(
    df["Date"],
    df["SP500_norm"],
    label="S&P 500",
    color="#BC13FE",
    linewidth=2
)

plt.title("Strategy vs S&P 500 (Normalized)", fontsize=14, pad=20)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Growth (Start = 1)", fontsize=12)

plt.grid(True, linestyle="--", alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig("strategy_vs_benchmarks_normalized.png", dpi=300)
plt.show()
