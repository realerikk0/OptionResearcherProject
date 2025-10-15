"""Black-Scholes Greeks utilities."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Literal, Tuple

import numpy as np
import pandas as pd
from scipy.stats import norm

OptionType = Literal["call", "put"]


@dataclass
class Greeks:
    """Greeks container for a single option quote."""

    delta: float
    gamma: float
    vega: float
    theta: float


def _ensure_time_to_expiry(expiration: pd.Series, current_date: pd.Series) -> np.ndarray:
    """Return time to expiry in years."""
    delta_days = (pd.to_datetime(expiration) - pd.to_datetime(current_date)).dt.days.clip(lower=0)
    return delta_days.to_numpy(dtype=float) / 365.0


def _d1_d2(
    spot: np.ndarray,
    strike: np.ndarray,
    ttm: np.ndarray,
    rate: np.ndarray,
    vol: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute Black-Scholes d1 and d2."""
    vol = np.clip(vol, 1e-6, None)
    sqrt_t = np.sqrt(np.clip(ttm, 1e-8, None))
    log_term = np.log(np.clip(spot, 1e-12, None) / np.clip(strike, 1e-12, None))
    d1 = (log_term + (rate + 0.5 * vol**2) * ttm) / (vol * sqrt_t)
    d2 = d1 - vol * sqrt_t
    return d1, d2


def bs_price(
    spot: float,
    strike: float,
    ttm: float,
    rate: float,
    vol: float,
    option_type: OptionType,
) -> float:
    """Black-Scholes option price."""
    if ttm <= 0:
        intrinsic = max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)
        return intrinsic

    d1, d2 = _d1_d2(
        np.array([spot], dtype=float),
        np.array([strike], dtype=float),
        np.array([ttm], dtype=float),
        np.array([rate], dtype=float),
        np.array([vol], dtype=float),
    )
    if option_type == "call":
        price = spot * norm.cdf(d1[0]) - strike * math.exp(-rate * ttm) * norm.cdf(d2[0])
    else:
        price = strike * math.exp(-rate * ttm) * norm.cdf(-d2[0]) - spot * norm.cdf(-d1[0])
    return max(float(price), 0.0)


def bs_greeks(
    spot: Iterable[float],
    strike: Iterable[float],
    ttm: Iterable[float],
    rate: Iterable[float],
    vol: Iterable[float],
    option_type: Iterable[OptionType],
) -> Greeks:
    """Return Greeks for iterables; kept for compatibility with dataclass usage."""
    spot_arr = np.asarray(spot, dtype=float)
    strike_arr = np.asarray(strike, dtype=float)
    ttm_arr = np.asarray(ttm, dtype=float)
    rate_arr = np.asarray(rate, dtype=float)
    vol_arr = np.asarray(vol, dtype=float)
    types = np.asarray(list(option_type))

    d1, d2 = _d1_d2(spot_arr, strike_arr, ttm_arr, rate_arr, vol_arr)
    sqrt_t = np.sqrt(np.clip(ttm_arr, 1e-8, None))
    pdf_d1 = norm.pdf(d1)
    discount = np.exp(-rate_arr * ttm_arr)

    gamma = pdf_d1 / (spot_arr * vol_arr * sqrt_t)
    vega = spot_arr * pdf_d1 * sqrt_t
    call_delta = norm.cdf(d1)
    put_delta = call_delta - 1

    theta_call = (
        -(spot_arr * pdf_d1 * vol_arr) / (2 * sqrt_t)
        - rate_arr * strike_arr * discount * norm.cdf(d2)
    )
    theta_put = (
        -(spot_arr * pdf_d1 * vol_arr) / (2 * sqrt_t)
        + rate_arr * strike_arr * discount * norm.cdf(-d2)
    )

    delta = np.where(types == "call", call_delta, put_delta)
    theta = np.where(types == "call", theta_call, theta_put)

    return Greeks(
        delta=np.nan_to_num(delta).mean(),
        gamma=np.nan_to_num(gamma).mean(),
        vega=np.nan_to_num(vega).mean(),
        theta=np.nan_to_num(theta).mean(),
    )


def compute_greeks_dataframe(
    options: pd.DataFrame,
    rates: pd.DataFrame,
    rate_column: str = "rate_10y",
) -> pd.DataFrame:
    """Augment option DataFrame with Black-Scholes Greeks."""
    df = options.copy()
    rate_lookup = dict(zip(pd.to_datetime(rates["date"]).dt.date, rates[rate_column]))
    df["risk_free"] = df["date"].map(rate_lookup).fillna(np.mean(list(rate_lookup.values())))
    df["ttm"] = _ensure_time_to_expiry(df["expiration"], df["date"])

    d1, d2 = _d1_d2(
        df["underlying_price"].to_numpy(),
        df["strike"].to_numpy(),
        df["ttm"].to_numpy(),
        df["risk_free"].to_numpy(),
        df["implied_volatility"].to_numpy(),
    )
    sqrt_t = np.sqrt(np.clip(df["ttm"].to_numpy(), 1e-8, None))
    pdf_d1 = norm.pdf(d1)
    discount = np.exp(-df["risk_free"].to_numpy() * df["ttm"].to_numpy())

    call_delta = norm.cdf(d1)
    put_delta = call_delta - 1
    df["delta"] = np.where(df["option_type"] == "call", call_delta, put_delta)
    df["gamma"] = pdf_d1 / (
        np.clip(df["underlying_price"].to_numpy(), 1e-12, None)
        * np.clip(df["implied_volatility"].to_numpy(), 1e-6, None)
        * sqrt_t
    )
    df["vega"] = df["underlying_price"].to_numpy() * pdf_d1 * sqrt_t

    theta_call = (
        -(df["underlying_price"].to_numpy() * pdf_d1 * df["implied_volatility"].to_numpy())
        / (2 * sqrt_t)
        - df["risk_free"].to_numpy()
        * df["strike"].to_numpy()
        * discount
        * norm.cdf(d2)
    )
    theta_put = (
        -(df["underlying_price"].to_numpy() * pdf_d1 * df["implied_volatility"].to_numpy())
        / (2 * sqrt_t)
        + df["risk_free"].to_numpy()
        * df["strike"].to_numpy()
        * discount
        * norm.cdf(-d2)
    )
    df["theta"] = np.where(df["option_type"] == "call", theta_call, theta_put)
    return df
