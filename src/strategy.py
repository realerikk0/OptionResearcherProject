"""Strategy definitions for option arbitrage research."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal

import numpy as np
import pandas as pd

TradeDirection = Literal["long", "short"]


@dataclass
class TradeSignal:
    """Trading signal for an arbitrage opportunity."""

    date: pd.Timestamp
    strategy: str
    direction: TradeDirection
    expected_edge: float
    cost_estimate: float
    net_edge: float
    metadata: dict


def generate_parity_trades(parity_df: pd.DataFrame, transaction_cost_bps: float = 10.0) -> pd.DataFrame:
    """Create trades from put-call parity deviations."""
    if parity_df.empty:
        return pd.DataFrame(columns=[field.name for field in TradeSignal.__dataclass_fields__.values()])

    df = parity_df.copy()
    spread = (df["call_ask"] - df["call_bid"]) + (df["put_ask"] - df["put_bid"])
    df["transaction_cost"] = 0.05 * spread + (
        (df["call_ask"] + df["put_ask"]) * (transaction_cost_bps / 10000.0)
    )
    df["expected_edge"] = np.abs(df["parity_diff"])
    df["net_edge"] = df["expected_edge"] - df["transaction_cost"]
    df["direction"] = np.where(df["parity_diff"] > 0, "short_combo", "long_combo")
    signals = []
    for row in df.itertuples():
        if not row.parity_flag:
            continue
        signals.append(
            TradeSignal(
                date=pd.to_datetime(row.date),
                strategy="put_call_parity",
                direction=row.direction,  # type: ignore[arg-type]
                expected_edge=float(row.expected_edge),
                cost_estimate=float(row.transaction_cost),
                net_edge=float(row.net_edge),
                metadata={
                    "strike": row.strike,
                    "expiration": row.expiration,
                    "parity_diff_pct": row.parity_diff_pct,
                },
            )
        )
    return pd.DataFrame([s.__dict__ for s in signals])


def generate_term_structure_trades(
    options_df: pd.DataFrame,
    iv_threshold: float = 0.05,
    notionals: float = 100.0,
) -> pd.DataFrame:
    """Calendar spread / vol-arb signals based on IV term structure."""
    if options_df.empty:
        return pd.DataFrame(columns=[field.name for field in TradeSignal.__dataclass_fields__.values()])

    grouped = (
        options_df.groupby(["date", "expiration"])
        .agg(mean_iv=("implied_volatility", "mean"), price=("underlying_price", "mean"))
        .reset_index()
    )

    signals: List[TradeSignal] = []
    for date, chunk in grouped.groupby("date"):
        if len(chunk) < 2:
            continue
        hottest = chunk.loc[chunk["mean_iv"].idxmax()]
        coldest = chunk.loc[chunk["mean_iv"].idxmin()]
        iv_spread = hottest["mean_iv"] - coldest["mean_iv"]
        if iv_spread <= iv_threshold:
            continue

        expected_edge = iv_spread * notionals
        cost_estimate = 0.02 * notionals
        net_edge = expected_edge - cost_estimate

        signals.append(
            TradeSignal(
                date=pd.to_datetime(date),
                strategy="calendar_vol_spread",
                direction="short",
                expected_edge=float(expected_edge),
                cost_estimate=float(cost_estimate),
                net_edge=float(net_edge),
                metadata={
                    "sell_expiration": hottest["expiration"],
                    "buy_expiration": coldest["expiration"],
                    "iv_spread": float(iv_spread),
                },
            )
        )
    return pd.DataFrame([s.__dict__ for s in signals])
