"""
End-to-end analysis pipeline for the Option Researcher project.

Steps:
1. Load synthetic dataset from data/raw.
2. Compute Black-Scholes Greeks.
3. Detect anomalies (Put-Call parity, IV smile/skew, Greeks outliers).
4. Generate arbitrage trade signals.
5. Backtest strategies and produce summary metrics.
6. Persist key tables to outputs/ for inspection.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.anomaly_detector import AnomalySummary, summarize_anomalies  # noqa: E402
from src.backtest import backtest_from_signals  # noqa: E402
from src.greeks_calculator import compute_greeks_dataframe  # noqa: E402
from src.strategy import generate_parity_trades, generate_term_structure_trades  # noqa: E402

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_dataset() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    options = pd.read_csv(DATA_DIR / "spy_option_chain.csv", parse_dates=["date", "expiration"])
    underlying = pd.read_csv(DATA_DIR / "spy_underlying.csv", parse_dates=["date"])
    rates = pd.read_csv(DATA_DIR / "treasury_rates.csv", parse_dates=["date"])
    return options, underlying, rates


def compute_and_flag(options: pd.DataFrame, rates: pd.DataFrame) -> tuple[pd.DataFrame, AnomalySummary]:
    enriched = compute_greeks_dataframe(options, rates)
    anomalies = summarize_anomalies(enriched)
    return enriched, anomalies


def save_outputs(enriched: pd.DataFrame, anomalies: AnomalySummary) -> None:
    enriched.to_csv(OUTPUT_DIR / "options_with_greeks.csv", index=False)
    anomalies.put_call_parity.to_csv(OUTPUT_DIR / "anomaly_put_call_parity.csv", index=False)
    anomalies.iv_smile_skew.to_csv(OUTPUT_DIR / "anomaly_iv_smile.csv", index=False)
    anomalies.greeks_outliers.to_csv(OUTPUT_DIR / "anomaly_greeks.csv", index=False)


def build_strategy_signals(enriched: pd.DataFrame, anomalies: AnomalySummary) -> pd.DataFrame:
    parity_signals = generate_parity_trades(anomalies.put_call_parity)
    term_signals = generate_term_structure_trades(enriched)

    parity_signals.to_csv(OUTPUT_DIR / "signals_parity.csv", index=False)
    term_signals.to_csv(OUTPUT_DIR / "signals_term_structure.csv", index=False)

    combined = pd.concat([parity_signals, term_signals], ignore_index=True)
    combined.to_csv(OUTPUT_DIR / "signals_combined.csv", index=False)
    return combined


def run_backtests(signals: pd.DataFrame) -> dict:
    results = {}
    for strategy_name, subset in signals.groupby("strategy"):
        results[strategy_name] = backtest_from_signals(subset)
    if not signals.empty:
        results["combined"] = backtest_from_signals(signals)
    return results


def export_metrics(results: dict) -> None:
    metrics = {}
    for name, result in results.items():
        metrics[name] = {
            "total_return": result.total_return,
            "annualized_return": result.annualized_return,
            "sharpe_ratio": result.sharpe_ratio,
            "max_drawdown": result.max_drawdown,
            "win_rate": result.win_rate,
        }
        result.daily_pnl.to_csv(OUTPUT_DIR / f"pnl_{name}.csv", header=["pnl"])
    (OUTPUT_DIR / "backtest_metrics.json").write_text(json.dumps(metrics, indent=2))


def main() -> None:
    options, underlying, rates = load_dataset()
    enriched, anomalies = compute_and_flag(options, rates)
    save_outputs(enriched, anomalies)
    signals = build_strategy_signals(enriched, anomalies)
    results = run_backtests(signals)
    export_metrics(results)

    print("=== Greeks & Anomaly Summary ===")
    print(f"Options with Greeks: {len(enriched):,} rows; saved to outputs/options_with_greeks.csv")
    print(f"Parity anomalies flagged: {anomalies.put_call_parity['parity_flag'].sum()}")
    print(f"IV skew anomalies flagged: {anomalies.iv_smile_skew['iv_anomaly'].sum()}")
    print(f"Greeks delta anomalies flagged: {anomalies.greeks_outliers['delta_flag'].sum()}")
    print(f"Greeks gamma anomalies flagged: {anomalies.greeks_outliers['gamma_flag'].sum()}")

    print("\n=== Strategy Signals ===")
    print(signals.groupby("strategy")["net_edge"].agg(["count", "sum"]))

    print("\n=== Backtest Metrics ===")
    for name, result in results.items():
        print(
            f"{name}: total_return={result.total_return:.4f}, "
            f"ann_return={result.annualized_return:.4f}, "
            f"sharpe={result.sharpe_ratio:.2f}, "
            f"max_dd={result.max_drawdown:.2%}, "
            f"win_rate={result.win_rate:.2%}"
        )


if __name__ == "__main__":
    main()
