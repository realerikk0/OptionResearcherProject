"""Backtesting harness for evaluating option strategies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


@dataclass
class BacktestResult:
    """Aggregated metrics from a backtest run."""

    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float


class Strategy(Protocol):
    """Protocol for strategies compatible with the backtester."""

    def generate(self, market_state: dict) -> Iterable[dict]:
        ...


def run_backtest(strategy: Strategy, market_data: Iterable[dict]) -> BacktestResult:
    """Execute a toy backtest and return placeholder metrics."""
    # TODO: Implement backtest mechanics
    return BacktestResult(
        total_return=0.0,
        annualized_return=0.0,
        sharpe_ratio=0.0,
        max_drawdown=0.0,
        win_rate=0.0,
    )
