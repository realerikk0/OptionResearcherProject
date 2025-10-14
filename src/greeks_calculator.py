"""Greeks calculation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class PricingModel(Protocol):
    """Protocol defining the interface expected from pricing models."""

    def delta(self, *args, **kwargs) -> float:  # noqa: D401 - placeholder
        ...

    def gamma(self, *args, **kwargs) -> float:
        ...

    def vega(self, *args, **kwargs) -> float:
        ...

    def theta(self, *args, **kwargs) -> float:
        ...


@dataclass
class Greeks:
    """Container for option Greeks."""

    delta: float
    gamma: float
    vega: float
    theta: float


def compute_greeks(model: PricingModel, *args, **kwargs) -> Greeks:
    """Compute a Greeks snapshot via the supplied pricing model."""
    return Greeks(
        delta=model.delta(*args, **kwargs),
        gamma=model.gamma(*args, **kwargs),
        vega=model.vega(*args, **kwargs),
        theta=model.theta(*args, **kwargs),
    )
