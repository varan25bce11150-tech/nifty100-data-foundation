"""
Sprint 2 - Day 10
CAGR Engine

Implements:
- Revenue CAGR
- PAT CAGR
- EPS CAGR
- 3Y / 5Y / 10Y
- All Sprint edge cases
"""

from __future__ import annotations

from enum import Enum
from typing import Optional, Tuple


class CAGRFlag(str, Enum):
    NORMAL = "NORMAL"
    TURNAROUND = "TURNAROUND"
    DECLINE_TO_LOSS = "DECLINE_TO_LOSS"
    BOTH_NEGATIVE = "BOTH_NEGATIVE"
    ZERO_BASE = "ZERO_BASE"
    INSUFFICIENT = "INSUFFICIENT"


def calculate_cagr(
    start_value: float,
    end_value: float,
    years: int
) -> Tuple[Optional[float], CAGRFlag]:
    """
    Generic CAGR calculator.

    Returns
    -------
    (value, flag)
    """

    if years <= 0:
        return None, CAGRFlag.INSUFFICIENT

    if start_value == 0:
        return None, CAGRFlag.ZERO_BASE

    if start_value > 0 and end_value < 0:
        return None, CAGRFlag.DECLINE_TO_LOSS

    if start_value < 0 and end_value > 0:
        return None, CAGRFlag.TURNAROUND

    if start_value < 0 and end_value < 0:
        return None, CAGRFlag.BOTH_NEGATIVE

    cagr = ((end_value / start_value) ** (1 / years) - 1) * 100

    return round(cagr, 2), CAGRFlag.NORMAL


def revenue_cagr(
    start_sales: float,
    end_sales: float,
    years: int
):
    return calculate_cagr(
        start_sales,
        end_sales,
        years,
    )


def pat_cagr(
    start_pat: float,
    end_pat: float,
    years: int
):
    return calculate_cagr(
        start_pat,
        end_pat,
        years,
    )


def eps_cagr(
    start_eps: float,
    end_eps: float,
    years: int
):
    return calculate_cagr(
        start_eps,
        end_eps,
        years,
    )


def revenue_cagr_3yr(start, end):
    return revenue_cagr(start, end, 3)


def revenue_cagr_5yr(start, end):
    return revenue_cagr(start, end, 5)


def revenue_cagr_10yr(start, end):
    return revenue_cagr(start, end, 10)


def pat_cagr_3yr(start, end):
    return pat_cagr(start, end, 3)


def pat_cagr_5yr(start, end):
    return pat_cagr(start, end, 5)


def pat_cagr_10yr(start, end):
    return pat_cagr(start, end, 10)


def eps_cagr_3yr(start, end):
    return eps_cagr(start, end, 3)


def eps_cagr_5yr(start, end):
    return eps_cagr(start, end, 5)


def eps_cagr_10yr(start, end):
    return eps_cagr(start, end, 10)