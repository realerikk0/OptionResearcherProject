"""Backtesting harness for evaluating option strategies."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    """Aggregated metrics from a backtest run."""

    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    daily_pnl: pd.Series


def _max_drawdown(cumulative_returns: pd.Series) -> float:
    running_max = cumulative_returns.cummax()
    drawdown = cumulative_returns / running_max - 1.0
    return float(drawdown.min())


def backtest_from_signals(
    signals: pd.DataFrame,
    initial_capital: float = 100_000.0,
    max_trades_per_day: int = 3,
) -> BacktestResult:
    """
    Evaluate a strategy using generated trade signals.

    The function assumes `signals` contains columns:
    - date
    - net_edge (expected profit after costs, in dollars)
    """
    if signals.empty:
        empty_series = pd.Series(dtype=float)
        return BacktestResult(
            total_return=0.0,
            annualized_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            daily_pnl=empty_series,
        )

    df = signals.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["net_edge"] > 0].sort_values(["date", "net_edge"], ascending=[True, False])

    daily_pnl = (
        df.groupby("date")
        .head(max_trades_per_day)
        .groupby("date")["net_edge"]
        .sum()
        .reindex(
            pd.to_datetime(sorted(df["date"].unique())),
            fill_value=0.0,
        )
    )

    daily_returns = daily_pnl / initial_capital
    cumulative_return = (1 + daily_returns).cumprod()

    total_return = cumulative_return.iloc[-1] - 1 if not cumulative_return.empty else 0.0
    ann_return = (1 + daily_returns.mean()) ** 252 - 1 if len(daily_returns) > 0 else 0.0
    sharpe = (
        np.sqrt(252) * daily_returns.mean() / daily_returns.std(ddof=0)
        if daily_returns.std(ddof=0) not in (0, np.nan)
        else 0.0
    )
    max_dd = _max_drawdown(cumulative_return) if not cumulative_return.empty else 0.0
    win_rate = (daily_returns > 0).sum() / len(daily_returns) if len(daily_returns) > 0 else 0.0

    return BacktestResult(
        total_return=float(total_return),
        annualized_return=float(ann_return),
        sharpe_ratio=float(sharpe),
        max_drawdown=float(max_dd),
        win_rate=float(win_rate),
        daily_pnl=daily_pnl,
    )
