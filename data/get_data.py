"""
合成 SPY 期权研究数据生成脚本。

生成内容：
- data/raw/spy_underlying.csv   # 20 个交易日的日线行情
- data/raw/spy_option_chain.csv # 每日 3 个到期日、5 个行权价、call/put 期权
- data/raw/treasury_rates.csv   # 对应日期的无风险利率

数据经过精心构造，保证 README 中的任务可执行，并嵌入若干可检测的异常。
"""

from __future__ import annotations

import math
import warnings
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
from scipy.stats import norm

warnings.filterwarnings("ignore")

RAW_DIR = Path(__file__).resolve().parent / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

SEED = 1337
TRADING_DAYS = 20
EXPIRY_OFFSETS = [30, 45, 60]
MONEYNESS = [0.9, 0.95, 1.0, 1.05, 1.1]
RISK_FREE = 0.045
BASE_VOL = 0.22
VOL_TERM_ADJUST = {30: 0.0, 45: 0.05, 60: -0.03}
BASE_DATE = date(2025, 1, 6)  # 第一个交易日


def banner(message: str) -> None:
    print("\n" + "=" * 70)
    print(message)
    print("=" * 70)


def generate_trading_calendar() -> pd.DatetimeIndex:
    return pd.bdate_range(BASE_DATE, periods=TRADING_DAYS)


def simulate_underlying_path(dates: pd.DatetimeIndex, rng: np.random.Generator) -> pd.DataFrame:
    """生成 SPY 日线行情。"""
    drift = 0.0006
    vol = 0.015
    log_returns = rng.normal(loc=drift, scale=vol, size=len(dates))
    close_prices = 460 * np.exp(np.cumsum(log_returns))

    records: List[Dict[str, object]] = []
    for idx, current_date in enumerate(dates):
        close = float(close_prices[idx])
        daily_ret = log_returns[idx]
        open_price = close / math.exp(daily_ret / 2)
        high = max(open_price, close) * (1 + abs(daily_ret) + rng.uniform(0.001, 0.012))
        low = min(open_price, close) * (1 - abs(daily_ret) - rng.uniform(0.001, 0.009))
        volume = int(rng.integers(4_500_000, 8_500_000))

        records.append(
            {
                "date": current_date.date(),
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "volume": volume,
            }
        )

    return pd.DataFrame(records)


def black_scholes_price(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
    """Black-Scholes 定价。"""
    if T <= 0:
        intrinsic = max(S - K, 0.0) if option_type == "call" else max(K - S, 0.0)
        return intrinsic

    if sigma <= 0:
        sigma = 1e-6

    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    if option_type == "call":
        price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    return max(price, 0.01)


def build_option_chain(
    dates: pd.DatetimeIndex,
    underlying: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """构造期权数据，嵌入轻微异常。"""
    rows: List[Dict[str, object]] = []
    price_lookup = dict(zip(underlying["date"], underlying["close"]))

    for current_date in dates:
        underlying_price = float(price_lookup[current_date.date()])
        for offset in EXPIRY_OFFSETS:
            expiration = (current_date + timedelta(days=offset)).date()
            T = (expiration - current_date.date()).days / 365.0
            base_sigma = BASE_VOL + VOL_TERM_ADJUST.get(offset, 0.0)

            for m in MONEYNESS:
                strike = round(underlying_price * m, 2)
                local_sigma = base_sigma * (1 + rng.normal(0, 0.05))
                local_sigma = max(local_sigma, 0.05)

                spread_bps = max(0.01, 0.012 * abs(m - 1) + 0.005)
                spread = 0.5 + spread_bps * underlying_price

                for option_type in ("call", "put"):
                    theo = black_scholes_price(
                        S=underlying_price, K=strike, T=T, r=RISK_FREE, sigma=local_sigma, option_type=option_type
                    )

                    mid = theo * (1 + rng.normal(0, 0.01))
                    gap = spread
                    bid = max(mid - gap / 2, 0.01)
                    ask = bid + gap
                    last = float(np.clip(mid + rng.normal(0, gap / 6), bid, ask))

                    volume = int(rng.integers(300, 5000))
                    open_interest = int(volume + rng.integers(200, 4000))

                    contract_symbol = (
                        f"SPY{expiration.strftime('%y%m%d')}"
                        f"{'C' if option_type == 'call' else 'P'}"
                        f"{int(strike * 1000):08d}"
                    )

                    rows.append(
                        {
                            "date": current_date.date(),
                            "underlying_price": round(underlying_price, 4),
                            "option_type": option_type,
                            "strike": round(strike, 2),
                            "expiration": expiration,
                            "bid": round(bid, 4),
                            "ask": round(ask, 4),
                            "last": round(last, 4),
                            "volume": volume,
                            "open_interest": open_interest,
                            "implied_volatility": round(local_sigma, 4),
                            "contract_symbol": contract_symbol,
                        }
                    )

    df = pd.DataFrame(rows)

    # Put-Call Parity 异常：抬高某天的 call 报价
    parity_mask = (
        (df["date"] == dates[3].date())
        & (df["option_type"] == "call")
        & np.isclose(df["strike"], price_lookup[dates[3].date()], atol=0.5)
    )
    df.loc[parity_mask, ["bid", "ask", "last"]] *= 1.12

    # 隐含波动率曲线异常：某个到期日整体抬升
    skew_mask = df["expiration"] == (dates[7] + timedelta(days=45)).date()
    df.loc[skew_mask, "implied_volatility"] *= 1.35

    # Greeks 异常示例：压低近月 out-of-the-money put 的隐含波
    greeks_mask = (
        (df["date"] == dates[10].date())
        & (df["option_type"] == "put")
        & (df["strike"] < price_lookup[dates[10].date()] * 0.95)
    )
    df.loc[greeks_mask, "implied_volatility"] *= 0.6

    return df


def build_treasury_curve(dates: pd.DatetimeIndex, rng: np.random.Generator) -> pd.DataFrame:
    base = RISK_FREE
    noise = rng.normal(0, 0.0005, size=len(dates))
    rates = base + np.cumsum(noise)
    return pd.DataFrame({"date": [d.date() for d in dates], "rate_10y": np.round(rates, 5)})


def save_csv(df: pd.DataFrame, filename: str) -> None:
    path = RAW_DIR / filename
    df.to_csv(path, index=False)
    print(f"  已保存到: {path.relative_to(Path.cwd())}")


def main() -> None:
    rng = np.random.default_rng(SEED)
    dates = generate_trading_calendar()

    banner("美股期权研究数据生成")

    underlying = simulate_underlying_path(dates, rng)
    save_csv(underlying, "spy_underlying.csv")

    option_chain = build_option_chain(dates, underlying, rng)
    save_csv(option_chain, "spy_option_chain.csv")

    treasury_rates = build_treasury_curve(dates, rng)
    save_csv(treasury_rates, "treasury_rates.csv")

    banner("数据摘要")
    print(f"  • 交易日数量: {len(underlying)}")
    print(f"  • 期权记录数: {len(option_chain)}")
    print(f"  • 国债利率点数: {len(treasury_rates)}")

    banner("示例概览")
    print("SPY 行情样例:")
    print(underlying.head(3).to_string(index=False))
    print("\n期权链样例:")
    print(option_chain.head(5).to_string(index=False))
    print("\n隐含波动率分布 (均值/最小/最大):")
    print(option_chain["implied_volatility"].describe()[["mean", "min", "max"]])


if __name__ == "__main__":
    main()
