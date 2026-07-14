"""
Sprint 2 - Day 11
Cash Flow KPI Engine

Computes:
- Free Cash Flow
- CFO/PAT Ratio
- CFO Quality Score
- CapEx Intensity
- CapEx Label
- FCF Conversion Rate
- Capital Allocation Pattern
"""

from __future__ import annotations

from typing import Optional
import csv
import logging

logger = logging.getLogger(__name__)


# ==========================================================
# FREE CASH FLOW
# ==========================================================

def free_cash_flow(
    operating_activity: float,
    investing_activity: float,
) -> Optional[float]:

    if operating_activity is None:
        return None

    if investing_activity is None:
        return None

    return round(
        operating_activity + investing_activity,
        2,
    )


# ==========================================================
# CFO / PAT RATIO
# ==========================================================

def cfo_pat_ratio(
    operating_activity: float,
    net_profit: float,
) -> Optional[float]:

    if operating_activity is None:
        return None

    if net_profit is None:
        return None

    if net_profit == 0:
        return None

    return round(
        operating_activity / net_profit,
        2,
    )


# ==========================================================
# CFO QUALITY
# ==========================================================

def cfo_quality_score(
    operating_activity: float,
    net_profit: float,
) -> Optional[str]:

    ratio = cfo_pat_ratio(
        operating_activity,
        net_profit,
    )

    if ratio is None:
        return None

    if ratio > 1:
        return "High Quality"

    if ratio >= 0.5:
        return "Moderate"

    return "Accrual Risk"


# ==========================================================
# CAPEX INTENSITY
# ==========================================================

def capex_intensity(
    investing_activity: float,
    sales: float,
) -> Optional[float]:

    if investing_activity is None:
        return None

    if sales is None:
        return None

    if sales == 0:
        return None

    return round(
        abs(investing_activity) / sales * 100,
        2,
    )


def capex_label(
    investing_activity: float,
    sales: float,
) -> Optional[str]:

    value = capex_intensity(
        investing_activity,
        sales,
    )

    if value is None:
        return None

    if value < 3:
        return "Asset Light"

    if value <= 8:
        return "Moderate"

    return "Capital Intensive"


# ==========================================================
# FCF CONVERSION
# ==========================================================

def fcf_conversion_rate(
    operating_activity: float,
    investing_activity: float,
    operating_profit: float,
) -> Optional[float]:

    if operating_activity is None:
        return None

    if investing_activity is None:
        return None

    if operating_profit is None:
        return None

    if operating_profit == 0:
        return None

    fcf = operating_activity + investing_activity

    return round(
        (fcf / operating_profit) * 100,
        2,
    )


# ==========================================================
# CAPITAL ALLOCATION
# ==========================================================

def _sign(value) -> str:

    if value is None:
        return "0"

    return "+" if value >= 0 else "-"


def capital_allocation_pattern(
    operating_activity: float,
    investing_activity: float,
    financing_activity: float,
    net_profit: float = 0,
):

    cfo = _sign(operating_activity)
    cfi = _sign(investing_activity)
    cff = _sign(financing_activity)

    pattern = "Mixed"

    if cfo == "+" and cfi == "-" and cff == "-":

        quality = cfo_quality_score(
            operating_activity,
            net_profit,
        )

        if quality == "High Quality":
            pattern = "Shareholder Returns"
        else:
            pattern = "Reinvestor"

    elif cfo == "+" and cfi == "+" and cff == "-":
        pattern = "Liquidating Assets"

    elif cfo == "-" and cfi == "+" and cff == "+":
        pattern = "Distress Signal"

    elif cfo == "-" and cfi == "-" and cff == "+":
        pattern = "Growth Funded by Debt"

    elif cfo == "+" and cfi == "+" and cff == "+":
        pattern = "Cash Accumulator"

    elif cfo == "-" and cfi == "-" and cff == "-":
        pattern = "Pre-Revenue"

    elif cfo == "+" and cfi == "-" and cff == "+":
        pattern = "Mixed"

    logger.info(
        "%s %s %s -> %s",
        cfo,
        cfi,
        cff,
        pattern,
    )

    return (
        pattern,
        cfo,
        cfi,
        cff,
    )


# ==========================================================
# CSV EXPORT
# ==========================================================

def write_capital_allocation_csv(
    rows,
    output_file="output/capital_allocation.csv",
):

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "company_id",
                "year",
                "cfo_sign",
                "cfi_sign",
                "cff_sign",
                "pattern_label",
            ]
        )

        for row in rows:

            pattern, cfo, cfi, cff = capital_allocation_pattern(
                row["operating_activity"],
                row["investing_activity"],
                row["financing_activity"],
                row.get("net_profit", 0),
            )

            writer.writerow(
                [
                    row["company_id"],
                    row["year"],
                    cfo,
                    cfi,
                    cff,
                    pattern,
                ]
            )

    logger.info(
        "capital_allocation.csv created successfully."
    )