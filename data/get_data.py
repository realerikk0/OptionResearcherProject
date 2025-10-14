"""
美股期权数据获取脚本
标的：SPY（S&P 500 ETF）
"""

from __future__ import annotations

import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

SYMBOL = "SPY"
END_DATE = datetime.utcnow().date()
START_DATE = END_DATE - timedelta(days=365)

RAW_DIR = Path(__file__).resolve().parent / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def banner(message: str) -> None:
    print("\n" + "=" * 70)
    print(message)
    print("=" * 70)


def get_underlying_data() -> pd.DataFrame:
    """获取 SPY 历史价格。"""
    print("\n[1/3] 获取 SPY ETF 历史价格...")
    spy = yf.Ticker(SYMBOL)
    df = spy.history(start=START_DATE, end=END_DATE + timedelta(days=1))
    if df.empty:
        df = spy.history(period="1y")
    df = df.reset_index().rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
            "Dividends": "dividends",
            "Stock Splits": "stock_splits",
        }
    )
    df = df[["date", "open", "high", "low", "close", "volume"]]
    print(f"✓ 获取到 {len(df)} 个交易日的数据")
    print(f"  日期范围: {df['date'].min()} 到 {df['date'].max()}")
    print(f"  价格范围: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    return df


def _filter_atm(options: pd.DataFrame, current_price: float, max_per_side: int = 10) -> pd.DataFrame:
    options = options.copy()
    options["distance_from_atm"] = (options["strike"] - current_price).abs()
    calls = options[options["option_type"] == "call"].nsmallest(max_per_side, "distance_from_atm")
    puts = options[options["option_type"] == "put"].nsmallest(max_per_side, "distance_from_atm")
    return pd.concat([calls, puts], ignore_index=True)


def get_option_chain_data(sample_size: int = 3) -> Optional[pd.DataFrame]:
    """获取 SPY 期权链数据。"""
    print("\n[2/3] 获取 SPY 期权链数据...")
    spy = yf.Ticker(SYMBOL)
    expirations: Iterable[str] = spy.options
    print(f"  找到 {len(expirations)} 个到期日")
    selected_expirations = list(expirations)[:sample_size]
    print(f"  将获取以下到期日的数据: {selected_expirations}")

    all_options: list[pd.DataFrame] = []
    current_price = None

    for exp_date in selected_expirations:
        try:
            print(f"\n  处理到期日: {exp_date}")
            opt_chain = spy.option_chain(exp_date)
            calls = opt_chain.calls.copy()
            calls["option_type"] = "call"
            calls["expiration"] = exp_date

            puts = opt_chain.puts.copy()
            puts["option_type"] = "put"
            puts["expiration"] = exp_date

            options = pd.concat([calls, puts], ignore_index=True)
            columns = [
                "contractSymbol",
                "strike",
                "lastPrice",
                "bid",
                "ask",
                "volume",
                "openInterest",
                "impliedVolatility",
                "option_type",
                "expiration",
            ]
            options = options[columns]

            options.columns = [
                "contract_symbol",
                "strike",
                "last",
                "bid",
                "ask",
                "volume",
                "open_interest",
                "implied_volatility",
                "option_type",
                "expiration",
            ]

            options["date"] = datetime.utcnow().strftime("%Y-%m-%d")

            if current_price is None:
                current_price = get_latest_spy_price()

            options["underlying_price"] = current_price

            filtered = _filter_atm(options, current_price)
            all_options.append(filtered)
            print(f"    ✓ 获取 {len(filtered)} 个期权合约")
        except Exception as exc:  # noqa: BLE001 - 日志用途
            print(f"    ✗ 失败: {exc}")

    if not all_options:
        return None

    df = pd.concat(all_options, ignore_index=True)
    df = df[
        [
            "date",
            "underlying_price",
            "option_type",
            "strike",
            "expiration",
            "bid",
            "ask",
            "last",
            "volume",
            "open_interest",
            "implied_volatility",
            "contract_symbol",
        ]
    ]
    print(f"\n✓ 总共获取 {len(df)} 条期权数据")
    return df


def get_latest_spy_price() -> float:
    spy = yf.Ticker(SYMBOL)
    last_close = spy.history(period="1d")["Close"].iloc[-1]
    return float(last_close)


def get_treasury_rates() -> pd.DataFrame:
    """获取美国 10 年期国债收益率。"""
    print("\n[3/3] 获取美国国债收益率（无风险利率）...")
    try:
        treasury = yf.Ticker("^TNX")
        df = treasury.history(start=START_DATE, end=END_DATE)
        df = df.reset_index()[["Date", "Close"]]
        df.columns = ["date", "rate_10y"]
        df["rate_10y"] = df["rate_10y"] / 100
        print(f"✓ 获取到 {len(df)} 个交易日的利率数据")
        print(f"  利率范围: {df['rate_10y'].min()*100:.2f}% - {df['rate_10y'].max()*100:.2f}%")
        return df
    except Exception as exc:  # noqa: BLE001 - 日志用途
        print(f"  ✗ 无法获取实时利率: {exc}")
        print("  使用固定利率: 4.5%")
        dates = pd.date_range(start=START_DATE, end=END_DATE, freq="D")
        return pd.DataFrame({"date": dates, "rate_10y": 0.045})


def save_csv(df: pd.DataFrame, filename: str) -> None:
    path = RAW_DIR / filename
    df.to_csv(path, index=False)
    print(f"  已保存到: {path.relative_to(Path.cwd())}")


def main() -> None:
    spy_data = get_underlying_data()
    save_csv(spy_data, "spy_underlying.csv")

    option_data = get_option_chain_data()
    if option_data is not None:
        save_csv(option_data, "spy_option_chain.csv")

    treasury_data = get_treasury_rates()
    save_csv(treasury_data, "treasury_rates.csv")

    banner("数据获取完成！")
    print("\n📊 数据摘要:")
    print(f"  • SPY价格数据: {len(spy_data)} 行")
    print(f"  • 期权链数据: {len(option_data) if option_data is not None else 0} 行")
    print(f"  • 国债利率数据: {len(treasury_data)} 行")
    print("\n📁 文件位置:")
    for name in ["spy_underlying.csv", "spy_option_chain.csv", "treasury_rates.csv"]:
        print(f"  • {RAW_DIR / name}")
    print("\n✅ 您现在可以开始分析了！")

    banner("数据质量检查")
    if option_data is not None:
        print("\n期权数据样例:")
        print(option_data.head(3))
        print("\n期权类型分布:")
        print(option_data["option_type"].value_counts())
        print("\n到期日分布:")
        print(option_data["expiration"].value_counts())
        print("\n隐含波动率统计:")
        print(f"  平均IV: {option_data['implied_volatility'].mean():.2%}")
        print(f"  IV范围: {option_data['implied_volatility'].min():.2%} - {option_data['implied_volatility'].max():.2%}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    banner("美股期权数据获取脚本 - SPY")
    main()
