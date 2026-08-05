"""
Sprint 5
Pros / Cons Rule Engine

Each rule returns either:

None

or

{
    "rule_id": "...",
    "type": "pro",
    "text": "...",
    "confidence": 85
}
"""

from __future__ import annotations

from typing import Dict, Optional

import pandas as pd

from .confidence import (
    score_combined,
    score_from_threshold,
)


# --------------------------------------------------------
# helper
# --------------------------------------------------------

RuleResult = Optional[Dict[str, object]]


def latest(df: pd.DataFrame):

    if df is None:
        return None

    if len(df) == 0:
        return None

    if "year" not in df.columns:
        return None

    return df.sort_values("year").iloc[-1]

def last_n(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return df.sort_values("year").tail(n)


def increasing(series: pd.Series) -> bool:

    values = pd.Series(series).dropna().tolist()

    if len(values) < 2:
        return False

    return all(
        values[i] > values[i - 1]
        for i in range(1, len(values))
    )

def decreasing(series: pd.Series) -> bool:

    values = pd.Series(series).dropna().tolist()

    if len(values) < 2:
        return False

    return all(
        values[i] < values[i - 1]
        for i in range(1, len(values))
    )

def build_result(
    rule_id: str,
    rule_type: str,
    text: str,
    confidence: int,
) -> RuleResult:

    if confidence <= 60:
        return None

    return {
        "rule_id": rule_id,
        "type": rule_type,
        "text": text,
        "confidence": confidence,
    }


# ======================================================
# PRO RULE 1
# ROE >20 for last 3 years
# ======================================================

def rule_pro_01(df: pd.DataFrame) -> RuleResult:

    if len(df) < 3:
        return None

    recent = last_n(df, 3)

    if (recent["return_on_equity_pct"] > 20).all():

        conf = score_combined(
            score_from_threshold(
                recent["return_on_equity_pct"].mean(),
                20,
            ),
            persistence_years=3,
        )

        return build_result(
            "PRO_01",
            "pro",
            (
                "Consistently high return on equity "
                "above 20% demonstrates exceptional "
                "capital efficiency."
            ),
            conf,
        )

    return None


# ======================================================
# PRO RULE 2
# FCF positive 5 years
# ======================================================

def rule_pro_02(df: pd.DataFrame) -> RuleResult:

    if len(df) < 5:
        return None

    recent = last_n(df, 5)

    if (recent["free_cash_flow_cr"] > 0).all():

        conf = score_combined(
            85,
            persistence_years=5,
        )

        return build_result(
            "PRO_02",
            "pro",
            (
                "Strong free cash flow generation "
                "over 5 years signals healthy "
                "business fundamentals."
            ),
            conf,
        )

    return None


# ======================================================
# PRO RULE 3
# Debt Free
# ======================================================

def rule_pro_03(df: pd.DataFrame) -> RuleResult:

    row = latest(df)
    if row is None:
        return None

    if row["debt_to_equity"] == 0:

        return build_result(
            "PRO_03",
            "pro",
            (
                "Debt-free balance sheet provides "
                "financial flexibility and eliminates "
                "interest burden."
            ),
            90,
        )

    return None


# ======================================================
# PRO RULE 4
# Revenue CAGR >15
# ======================================================

def rule_pro_04(df: pd.DataFrame) -> RuleResult:

    row = latest(df)
    if row is None:
        return None

    value = row["revenue_cagr_5yr"]

    if pd.notna(value) and value > 15:

        conf = score_from_threshold(
            value,
            15,
        )

        return build_result(
            "PRO_04",
            "pro",
            (
                "Revenue growing above 15% CAGR "
                "over 5 years reflects strong "
                "business momentum."
            ),
            conf,
        )

    return None


# ======================================================
# PRO RULE 5
# OPM >25
# ======================================================

def rule_pro_05(df: pd.DataFrame) -> RuleResult:

    row = latest(df)
    if row is None:
        return None

    value = row["operating_profit_margin_pct"]

    if pd.notna(value) and value > 25:

        conf = score_from_threshold(
            value,
            25,
        )

        return build_result(
            "PRO_05",
            "pro",
            (
                "Operating margin above 25% "
                "indicates strong pricing power "
                "and cost discipline."
            ),
            conf,
        )

    return None


# ======================================================
# PRO RULE 6
# PAT CAGR >20
# ======================================================

def rule_pro_06(df: pd.DataFrame) -> RuleResult:

    row = latest(df)
    if row is None:
        return None

    value = row["pat_cagr_5yr"]

    if pd.notna(value) and value > 20:

        conf = score_from_threshold(
            value,
            20,
        )

        return build_result(
            "PRO_06",
            "pro",
            (
                "Net profit compounding above "
                "20% over five years creates "
                "significant shareholder value."
            ),
            conf,
        )

    return None
# ======================================================
# PRO RULE 7
# ICR >10 OR Debt Free
# ======================================================

def rule_pro_07(df: pd.DataFrame) -> RuleResult:

    row = latest(df)
    if row is None:
        return None
    icr = row["interest_coverage"]
    label = str(row["icr_label"]).strip().lower()

    if (
        (pd.notna(icr) and icr > 10)
        or label == "debt free"
    ):

        conf = 88

        return build_result(
            "PRO_07",
            "pro",
            (
                "Very high interest coverage ratio "
                "reflects negligible financial stress "
                "from debt servicing."
            ),
            conf,
        )

    return None


# ======================================================
# PRO RULE 8
# Dividend >2% AND Positive FCF
# ======================================================

def rule_pro_08(
    ratios_df: pd.DataFrame,
    market_df: pd.DataFrame,
) -> RuleResult:

    if ratios_df.empty or market_df.empty:
        return None

    ratio = latest(ratios_df)
    market = latest(market_df)

    fcf = ratio["free_cash_flow_cr"]
    div = market["dividend_yield"]

    if (
        pd.notna(fcf)
        and pd.notna(div)
        and fcf > 0
        and div > 2
    ):

        return build_result(
            "PRO_08",
            "pro",
            (
                "Consistent dividend yield above "
                "2% backed by positive free cash flow."
            ),
            82,
        )

    return None


# ======================================================
# PRO RULE 9
# EPS CAGR >15
# ======================================================

def rule_pro_09(df: pd.DataFrame) -> RuleResult:

    row = latest(df)
    if row is None:
        return None

    eps = row["eps_cagr_5yr"]

    if pd.notna(eps) and eps > 15:

        conf = score_from_threshold(
            eps,
            15,
        )

        return build_result(
            "PRO_09",
            "pro",
            (
                "Earnings per share growing above "
                "15% CAGR indicates strong earnings "
                "quality and compounding."
            ),
            conf,
        )

    return None


# ======================================================
# PRO RULE 10
# ROE improving for 3 years
# ======================================================

def rule_pro_10(df: pd.DataFrame) -> RuleResult:

    if len(df) < 3:
        return None

    recent = last_n(df, 3)

    if increasing(recent["return_on_equity_pct"]):

        return build_result(
            "PRO_10",
            "pro",
            (
                "Return on equity improving for "
                "three consecutive years shows "
                "strengthening business quality."
            ),
            84,
        )

    return None


# ======================================================
# PRO RULE 11
# Revenue CAGR > PAT CAGR
# ======================================================

def rule_pro_11(df: pd.DataFrame) -> RuleResult:

    row = latest(df)
    if row is None:
        return None

    rev = row["revenue_cagr_5yr"]
    pat = row["pat_cagr_5yr"]

    if (
        pd.notna(rev)
        and pd.notna(pat)
        and pat > rev
    ):

        return build_result(
            "PRO_11",
            "pro",
            (
                "Revenue growing slower than profits "
                "shows improving operating leverage "
                "and scale benefits."
            ),
            86,
        )

    return None


# ======================================================
# PRO RULE 12
# Assets growing with declining debt
# ======================================================

def rule_pro_12(
    balance_df: pd.DataFrame,
) -> RuleResult:

    if len(balance_df) < 3:
        return None

    recent = last_n(balance_df, 3)

    assets_up = increasing(recent["total_assets"])

    debt_down = decreasing(recent["borrowings"])

    if assets_up and debt_down:

        return build_result(
            "PRO_12",
            "pro",
            (
                "Growing asset base funded by "
                "internal accruals reflects "
                "self-sustaining growth."
            ),
            88,
        )

    return None


# ======================================================
# Registry
# ======================================================

PRO_RULES = [
    rule_pro_01,
    rule_pro_02,
    rule_pro_03,
    rule_pro_04,
    rule_pro_05,
    rule_pro_06,
    rule_pro_07,
    rule_pro_08,
    rule_pro_09,
    rule_pro_10,
    rule_pro_11,
    rule_pro_12,
]

# ======================================================
# CON RULE 1
# Debt-to-Equity > 2 (Non Financial)
# ======================================================

def rule_con_01(df: pd.DataFrame) -> RuleResult:

    row = latest(df)
    if row is None:
        return None

    de = row["debt_to_equity"]

    if pd.notna(de) and de > 2:

        conf = score_from_threshold(
            de,
            2.0,
        )

        return build_result(
            "CON_01",
            "con",
            (
                f"Debt-to-equity ratio of {de:.2f} is elevated "
                "for a non-financial company and warrants monitoring."
            ),
            conf,
        )

    return None


# ======================================================
# CON RULE 2
# Negative FCF for 3 Years
# ======================================================

def rule_con_02(df: pd.DataFrame) -> RuleResult:

    if len(df) < 3:
        return None

    recent = last_n(df, 3)

    if (recent["free_cash_flow_cr"] < 0).all():

        return build_result(
            "CON_02",
            "con",
            (
                "Free cash flow negative for three consecutive years "
                "raises concern about cash generation quality."
            ),
            86,
        )

    return None


# ======================================================
# CON RULE 3
# OPM declining for 3 years
# ======================================================

def rule_con_03(df: pd.DataFrame) -> RuleResult:

    if len(df) < 3:
        return None

    recent = last_n(df, 3)

    if decreasing(
        recent["operating_profit_margin_pct"]
    ):

        return build_result(
            "CON_03",
            "con",
            (
                "Operating margins declining for three consecutive years "
                "suggest pricing or cost pressure."
            ),
            82,
        )

    return None


# ======================================================
# CON RULE 4
# Net Profit Negative
# ======================================================

def rule_con_04(
    profit_df: pd.DataFrame,
) -> RuleResult:

    if profit_df.empty:
        return None

    row = latest(profit_df)

    if row["net_profit"] < 0:

        return build_result(
            "CON_04",
            "con",
            (
                "Company reported a net loss in the most recent financial year."
            ),
            90,
        )

    return None


# ======================================================
# CON RULE 5
# Revenue declining 2 Years
# ======================================================

def rule_con_05(
    profit_df: pd.DataFrame,
) -> RuleResult:

    if len(profit_df) < 2:
        return None

    recent = last_n(profit_df, 2)

    if decreasing(
        recent["sales"]
    ):

        return build_result(
            "CON_05",
            "con",
            (
                "Revenue contraction over two consecutive years "
                "indicates demand weakness or market share loss."
            ),
            82,
        )

    return None


# ======================================================
# CON RULE 6
# ICR <1.5
# ======================================================

def rule_con_06(df: pd.DataFrame) -> RuleResult:

    row = latest(df)
    if row is None:
        return None

    icr = row["interest_coverage"]

    if pd.notna(icr) and icr < 1.5:

        conf = score_from_threshold(
            1.5,
            icr,
        )

        return build_result(
            "CON_06",
            "con",
            (
                "Interest coverage ratio below 1.5x indicates the "
                "company is at risk of not meeting its debt obligations."
            ),
            conf,
        )

    return None

# ======================================================
# CON RULE 7
# Dividend Payout > 100%
# ======================================================

def rule_con_07(
    profit_df: pd.DataFrame,
) -> RuleResult:

    if profit_df.empty:
        return None

    row = latest(profit_df)

    payout = row["dividend_payout"]

    if pd.notna(payout) and payout > 100:

        conf = score_from_threshold(
            payout,
            100,
        )

        return build_result(
            "CON_07",
            "con",
            (
                "Dividend payout ratio above 100% means the company "
                "is paying dividends from reserves, which is unsustainable."
            ),
            conf,
        )

    return None


# ======================================================
# CON RULE 8
# Debt-to-Equity Rising 3 Years
# ======================================================

def rule_con_08(df: pd.DataFrame) -> RuleResult:

    if len(df) < 3:
        return None

    recent = last_n(df, 3)

    if increasing(recent["debt_to_equity"]):

        return build_result(
            "CON_08",
            "con",
            (
                "Rising debt-to-equity ratio over three years suggests "
                "increasing financial leverage risk."
            ),
            82,
        )

    return None


# ======================================================
# CON RULE 9
# EPS Declining 3 Years
# ======================================================

def rule_con_09(
    profit_df: pd.DataFrame,
) -> RuleResult:

    if len(profit_df) < 3:
        return None

    recent = last_n(profit_df, 3)

    if decreasing(recent["eps"]):

        return build_result(
            "CON_09",
            "con",
            (
                "Earnings per share declining for three consecutive years "
                "reflects deteriorating profitability."
            ),
            84,
        )

    return None


# ======================================================
# CON RULE 10
# ROCE < 10%
# ======================================================

def rule_con_10(df: pd.DataFrame) -> RuleResult:

    row = latest(df)
    if row is None:
        return None

    roce = row["return_on_capital_employed_pct"]

    if pd.notna(roce) and roce < 10:

        conf = score_from_threshold(
            10,
            roce,
        )

        return build_result(
            "CON_10",
            "con",
            (
                "Return on capital employed below 10% suggests the "
                "business is not generating sufficient returns on invested capital."
            ),
            conf,
        )

    return None


# ======================================================
# CON RULE 11
# High Borrowings
# (Adapted because Net Debt / EBITDA is unavailable)
# ======================================================

def rule_con_11(
    balance_df: pd.DataFrame,
) -> RuleResult:

    if balance_df.empty:
        return None

    row = latest(balance_df)

    borrowings = row["borrowings"]
    assets = row["total_assets"]

    if (
        pd.notna(borrowings)
        and pd.notna(assets)
        and assets > 0
        and (borrowings / assets) > 0.50
    ):

        return build_result(
            "CON_11",
            "con",
            (
                "Borrowings constitute a significant proportion of total "
                "assets, reducing financial flexibility."
            ),
            78,
        )

    return None


# ======================================================
# CON RULE 12
# Revenue CAGR < 5%
# ======================================================

def rule_con_12(df: pd.DataFrame) -> RuleResult:

    row = latest(df)
    if row is None:
        return None

    cagr = row["revenue_cagr_5yr"]

    if pd.notna(cagr) and cagr < 5:

        conf = score_from_threshold(
            5,
            cagr,
        )

        return build_result(
            "CON_12",
            "con",
            (
                "Revenue growing below 5% CAGR over five years "
                "suggests limited business momentum."
            ),
            conf,
        )

    return None

# ======================================================
# CON RULE REGISTRY
# ======================================================

CON_RULES = [
    rule_con_01,
    rule_con_02,
    rule_con_03,
    rule_con_04,
    rule_con_05,
    rule_con_06,
    rule_con_07,
    rule_con_08,
    rule_con_09,
    rule_con_10,
    rule_con_11,
    rule_con_12,
]