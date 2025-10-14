"""Visualization helpers for Greeks and pricing anomalies."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt


def plot_iv_smile(strikes: list[float], implied_vols: list[float], *, title: str = "IV Smile") -> Any:
    """Render a simple IV smile chart."""
    fig, ax = plt.subplots()
    ax.plot(strikes, implied_vols, marker="o")
    ax.set_title(title)
    ax.set_xlabel("Strike")
    ax.set_ylabel("Implied Volatility")
    fig.tight_layout()
    return fig
