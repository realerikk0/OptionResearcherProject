"""Strategy definitions for option arbitrage research."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Signal:
    """Trading signal placeholder."""

    name: str
    direction: str
    size: float
    metadata: dict


class Strategy:
    """Base class for arbitrage strategies."""

    name = "base_strategy"

    def generate(self, market_state: dict) -> List[Signal]:
        """Produce trading signals given current market state."""
        raise NotImplementedError
