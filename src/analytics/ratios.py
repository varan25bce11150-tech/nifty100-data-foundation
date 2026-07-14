"""
Profitability Ratio Engine
Sprint 2 - Day 08 & Day 09

Implements:

Profitability:
- Net Profit Margin
- Operating Profit Margin
- ROE
- ROCE
- ROA
- OPM Cross Check

Leverage & Efficiency:
- Debt to Equity
- High Leverage Flag
- Interest Coverage Ratio
- Net Debt
- Asset Turnover
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ============================================================
# Utility
# ============================================================

def safe_divide(
    numerator: Optional[float],
    denominator: Optional[float]
) -> Optional[float]:

    if numerator is None or denominator is None:
        return None

    if denominator == 0:
        return None

    return numerator / denominator



# ============================================================
# Profitability Ratios
# ============================================================


def net_profit_margin(
    net_profit: float,
    sales: float
) -> Optional[float]:

    value = safe_divide(net_profit, sales)

    return None if value is None else round(value * 100, 2)



def operating_profit_margin(
    operating_profit: float,
    sales: float
) -> Optional[float]:

    value = safe_divide(
        operating_profit,
        sales
    )

    return None if value is None else round(value * 100, 2)



def return_on_equity(
    net_profit: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:

    equity = (equity_capital or 0) + (reserves or 0)

    if equity <= 0:
        return None

    return round(
        (net_profit / equity) * 100,
        2
    )



def return_on_capital_employed(
    operating_profit: float,
    interest: float,
    equity_capital: float,
    reserves: float,
    borrowings: float
) -> Optional[float]:

    capital = (
        (equity_capital or 0)
        +
        (reserves or 0)
        +
        (borrowings or 0)
    )

    if capital <= 0:
        return None


    ebit = (
        (operating_profit or 0)
        +
        (interest or 0)
    )


    return round(
        (ebit / capital) * 100,
        2
    )



def return_on_assets(
    net_profit: float,
    total_assets: float
) -> Optional[float]:

    value = safe_divide(
        net_profit,
        total_assets
    )

    return None if value is None else round(
        value * 100,
        2
    )



# ============================================================
# Validation
# ============================================================


def check_opm_difference(
    computed_opm: Optional[float],
    source_opm: Optional[float],
    company_id: str,
    year: int,
    tolerance: float = 1.0
) -> bool:


    if computed_opm is None or source_opm is None:
        return False


    difference = abs(
        computed_opm - source_opm
    )


    if difference > tolerance:

        logger.warning(
            "OPM mismatch | Company=%s Year=%s "
            "Computed=%.2f Source=%.2f Difference=%.2f",
            company_id,
            year,
            computed_opm,
            source_opm,
            difference
        )

        return True


    return False



def is_financial_sector(
    sector: Optional[str]
) -> bool:


    if not isinstance(sector, str):
        return False


    sector = sector.lower()


    keywords = [
        "bank",
        "financial",
        "finance",
        "insurance",
        "nbfc",
        "housing finance"
    ]


    return any(
        word in sector
        for word in keywords
    )



# ============================================================
# Leverage Ratios
# ============================================================


def debt_to_equity(
    borrowings: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:


    borrowings = borrowings or 0


    if borrowings == 0:
        return 0.0


    equity = (
        (equity_capital or 0)
        +
        (reserves or 0)
    )


    if equity <= 0:
        return None


    return round(
        borrowings / equity,
        2
    )



def high_leverage_flag(
    debt_to_equity_ratio: Optional[float],
    sector: Optional[str]
) -> bool:


    if debt_to_equity_ratio is None:
        return False


    if is_financial_sector(sector):
        return False


    return debt_to_equity_ratio > 5



def interest_coverage_ratio(
    operating_profit: float,
    other_income: float,
    interest: float
) -> Optional[float]:


    if interest is None or interest == 0:
        return None


    numerator = (
        (operating_profit or 0)
        +
        (other_income or 0)
    )


    return round(
        numerator / interest,
        2
    )



def interest_coverage_label(
    interest_coverage: Optional[float]
) -> str:


    if interest_coverage is None:
        return "Debt Free"


    return "Normal"



def interest_coverage_warning(
    interest_coverage: Optional[float]
) -> bool:


    if interest_coverage is None:
        return False


    return interest_coverage < 1.5



def net_debt(
    borrowings: float,
    investments: float
) -> float:


    return round(
        (borrowings or 0)
        -
        (investments or 0),
        2
    )



def asset_turnover(
    sales: float,
    total_assets: float
) -> Optional[float]:


    value = safe_divide(
        sales,
        total_assets
    )


    return None if value is None else round(
        value,
        2
    )