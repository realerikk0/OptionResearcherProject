"""Detect anomalies in option Greeks, IV structure, and parity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Protocol


@dataclass
class OptionSnapshot:
    """Minimal option snapshot used for anomaly scanning."""

    contract_symbol: str
    option_type: str
    strike: float
    expiration: str
    underlying_price: float
    bid: float
    ask: float
    implied_volatility: float
    delta: float
    gamma: float
    vega: float
    theta: float


class AnomalyRule(Protocol):
    """Protocol for anomaly detection rules."""

    def evaluate(self, option: OptionSnapshot) -> bool:
        ...


def run_rules(options: Iterable[OptionSnapshot], rules: Iterable[AnomalyRule]) -> List[OptionSnapshot]:
    """Return options that violate any provided anomaly rule."""
    flagged: List[OptionSnapshot] = []
    for option in options:
        if any(rule.evaluate(option) for rule in rules):
            flagged.append(option)
    return flagged
