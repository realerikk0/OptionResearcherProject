"""Detect anomalies in option Greeks, IV structure, and parity."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class AnomalySummary:
    """Container holding anomaly flags and supporting metrics."""

    put_call_parity: pd.DataFrame
    iv_smile_skew: pd.DataFrame
    greeks_outliers: pd.DataFrame


def detect_put_call_parity(df: pd.DataFrame, threshold: float = 0.01) -> pd.DataFrame:
    """Flag deviations from put-call parity greater than the supplied threshold."""
    parity_df = df.copy()
    parity_df["parity_theoretical"] = (
        parity_df["underlying_price"]
        - parity_df["strike"] * np.exp(-parity_df["risk_free"] * parity_df["ttm"])
    )
    call_prices = (
        parity_df[parity_df["option_type"] == "call"]
        .set_index(["date", "strike", "expiration"])
        [["last", "bid", "ask", "parity_theoretical"]]
        .rename(columns={"last": "call_last", "bid": "call_bid", "ask": "call_ask"})
    )
    put_prices = (
        parity_df[parity_df["option_type"] == "put"]
        .set_index(["date", "strike", "expiration"])
        [["last", "bid", "ask"]]
        .rename(columns={"last": "put_last", "bid": "put_bid", "ask": "put_ask"})
    )

    merged = call_prices.join(put_prices, how="inner")
    merged["parity_observed"] = merged["call_last"] - merged["put_last"]
    merged["parity_diff"] = merged["parity_observed"] - merged["parity_theoretical"]
    merged["parity_diff_pct"] = merged["parity_diff"] / merged["parity_theoretical"].replace(0, np.nan)
    merged["parity_flag"] = merged["parity_diff_pct"].abs() > threshold
    return merged.reset_index()


def detect_iv_skew(df: pd.DataFrame, z_threshold: float = 1.8) -> pd.DataFrame:
    """Flag implied volatility smiles / skews using z-scores across strikes."""
    smile = df.copy()
    smile["iv_zscore"] = smile.groupby(["date", "expiration", "option_type"])["implied_volatility"].transform(
        lambda x: (x - x.mean()) / (x.std(ddof=0) if x.std(ddof=0) not in (0, np.nan) else np.nan)
    )
    smile["iv_zscore"] = smile["iv_zscore"].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    smile["iv_anomaly"] = smile["iv_zscore"].abs() > z_threshold
    return smile[
        [
            "date",
            "expiration",
            "option_type",
            "strike",
            "implied_volatility",
            "iv_zscore",
            "iv_anomaly",
        ]
    ]


def detect_greeks_outliers(
    df: pd.DataFrame,
    delta_deviation: float = 0.03,
    gamma_ratio_threshold: float = 1.5,
) -> pd.DataFrame:
    """Flag anomalous Greeks values based on heuristics."""
    enriched = df.copy()
    atm_mask = np.isclose(enriched["strike"], enriched["underlying_price"], rtol=0.02)
    enriched["delta_expected"] = np.where(
        atm_mask & (enriched["option_type"] == "call"),
        0.5,
        np.where(atm_mask & (enriched["option_type"] == "put"), -0.5, np.nan),
    )
    enriched["delta_deviation"] = enriched["delta"] - enriched["delta_expected"]
    enriched["delta_flag"] = atm_mask & (
        np.abs(enriched["delta_deviation"].fillna(0.0)) > delta_deviation
    )

    gamma_median = (
        enriched.groupby(["date", "expiration"])["gamma"].transform("median").replace(0, np.nan)
    )
    enriched["gamma_ratio"] = enriched["gamma"] / gamma_median
    enriched["gamma_flag"] = np.abs(enriched["gamma_ratio"]).fillna(0.0) > gamma_ratio_threshold
    return enriched[
        [
            "date",
            "expiration",
            "contract_symbol",
            "option_type",
            "strike",
            "delta",
            "gamma",
            "delta_flag",
            "gamma_flag",
        ]
    ]


def summarize_anomalies(df: pd.DataFrame) -> AnomalySummary:
    """Return all anomaly tables in a single dataclass."""
    return AnomalySummary(
        put_call_parity=detect_put_call_parity(df),
        iv_smile_skew=detect_iv_skew(df),
        greeks_outliers=detect_greeks_outliers(df),
    )
