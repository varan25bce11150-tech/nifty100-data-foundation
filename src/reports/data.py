"""
Sprint 7 - Day 42
Report Data Access

Shared SQLite loaders used by the generated financial reports.

Every loader is restricted to the authoritative 92-company universe
(`companies`), matching the convention established in earlier sprints.
Sector information always comes from the `sectors` table via a JOIN,
never from `companies` columns.

All helpers are defensive:
- years are extracted with `extract_year`, so integer years (financial
  ratios, market cap) and text years ("Mar 2024", "Mar-13") both work;
- companies with missing data (e.g. SBIN has no financial_ratios,
  ATGL has no cashflow) are kept with NaN values rather than dropped.
"""

from __future__ import annotations

import os
import sqlite3
from typing import List, Optional

import pandas as pd

from src.analytics.year_utils import extract_year


# ==========================================================
# CONFIGURATION
# ==========================================================

DB_PATH = "nifty100.db"

EXPECTED_COMPANY_COUNT = 92

OUTPUT_DIR = "output"

CLUSTER_LABEL_FILE = os.path.join(OUTPUT_DIR, "cluster_labels.csv")

RATIO_FIELDS = [
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "return_on_assets_pct",
    "debt_to_equity",
    "interest_coverage",
    "free_cash_flow_cr",
    "revenue_cagr_5yr",
    "composite_quality_score",
]


# ==========================================================
# UNIVERSE VALIDATION
# ==========================================================

def validate_universe(data: pd.DataFrame) -> None:
    """Validate the authoritative company universe.

    Raises ValueError if the row count is not the expected 92 or if
    company ids are duplicated. Every report pipeline calls this before
    generating output.
    """
    if len(data) != EXPECTED_COMPANY_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_COMPANY_COUNT} companies in the authoritative "
            f"universe, but found {len(data)}."
        )

    if data["company_id"].nunique() != EXPECTED_COMPANY_COUNT:
        raise ValueError(
            "Duplicate company ids found in the authoritative universe."
        )


# ==========================================================
# LOW-LEVEL LOADERS
# ==========================================================

def load_companies(db_path: str = DB_PATH) -> pd.DataFrame:
    """Load the 92 companies joined with their sector information.

    Returns one row per company with company_id, company_name,
    broad_sector, industry and market_cap_category.
    """
    conn = sqlite3.connect(db_path)

    try:
        data = pd.read_sql_query(
            """
            SELECT
                c.id AS company_id,
                c.company_name,
                s.sector AS broad_sector,
                s.industry AS industry,
                s.market_cap_category
            FROM companies c
            LEFT JOIN sectors s
                ON c.id = s.company_id
            ORDER BY c.id
            """,
            conn,
        )
    finally:
        conn.close()

    data["company_name"] = data["company_name"].fillna("").str.strip()

    return data


def load_ratios_history(db_path: str = DB_PATH) -> pd.DataFrame:
    """Load the full financial_ratios history.

    A `calendar_year` column (extracted safely from `year`) is added so
    text and integer years are handled identically downstream.
    """
    conn = sqlite3.connect(db_path)

    try:
        data = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
    finally:
        conn.close()

    data["calendar_year"] = data["year"].apply(extract_year)

    return data


def load_pnl_history(db_path: str = DB_PATH) -> pd.DataFrame:
    """Load profitandloss history with extracted calendar years."""
    conn = sqlite3.connect(db_path)

    try:
        data = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                sales,
                expenses,
                operating_profit,
                net_profit,
                eps,
                dividend_payout
            FROM profitandloss
            """,
            conn,
        )
    finally:
        conn.close()

    data["calendar_year"] = data["year"].apply(extract_year)

    return data


def load_cashflow_history(db_path: str = DB_PATH) -> pd.DataFrame:
    """Load cashflow history with extracted calendar years."""
    conn = sqlite3.connect(db_path)

    try:
        data = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                operating_activity,
                investing_activity,
                financing_activity,
                net_cash_flow
            FROM cashflow
            """,
            conn,
        )
    finally:
        conn.close()

    data["calendar_year"] = data["year"].apply(extract_year)

    return data


def load_market_cap_history(db_path: str = DB_PATH) -> pd.DataFrame:
    """Load market_cap history with extracted calendar years."""
    conn = sqlite3.connect(db_path)

    try:
        data = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                market_cap,
                enterprise_value,
                pe_ratio,
                pb_ratio,
                dividend_yield
            FROM market_cap
            """,
            conn,
        )
    finally:
        conn.close()

    data["calendar_year"] = data["year"].apply(extract_year)

    return data


def load_sector_names(db_path: str = DB_PATH) -> List[str]:
    """Return the distinct sector names in the sectors table.

    Order is by descending company count so the largest sectors appear
    first in batch generation output.
    """
    conn = sqlite3.connect(db_path)

    try:
        rows = conn.execute(
            """
            SELECT sector, COUNT(*) AS company_count
            FROM sectors
            WHERE sector IS NOT NULL
            GROUP BY sector
            ORDER BY company_count DESC, sector
            """
        ).fetchall()
    finally:
        conn.close()

    return [row[0] for row in rows]


def load_prosandcons(db_path: str = DB_PATH) -> pd.DataFrame:
    """Load the generated pros & cons summaries."""
    conn = sqlite3.connect(db_path)

    try:
        data = pd.read_sql_query(
            """
            SELECT company_id, pros, cons
            FROM prosandcons
            """,
            conn,
        )
    finally:
        conn.close()

    return data


def load_cluster_labels(
    cluster_label_file: Optional[str] = CLUSTER_LABEL_FILE,
) -> pd.DataFrame:
    """Load Sprint 6 cluster labels if the generated CSV exists.

    Cluster labels are an optional enrichment: the reports work from the
    database alone. When `output/cluster_labels.csv` is present the
    cluster assignment is merged into the portfolio summary; otherwise an
    empty DataFrame is returned.
    """
    if not cluster_label_file or not os.path.exists(cluster_label_file):
        return pd.DataFrame(columns=["company_id", "cluster_id", "cluster_name"])

    return pd.read_csv(cluster_label_file)


# ==========================================================
# LATEST SNAPSHOT
# ==========================================================

def _latest_rows(data: pd.DataFrame) -> pd.DataFrame:
    """Keep the most recent row per company using extracted years.

    Rows without an extractable year (e.g. TTM) sort last and therefore
    represent the most recent period when present.
    """
    result = data.copy()
    result = result.sort_values(
        ["company_id", "calendar_year"],
        na_position="last",
    )
    return result.drop_duplicates(subset=["company_id"], keep="last")


def load_latest_snapshot(db_path: str = DB_PATH) -> pd.DataFrame:
    """Build one row per company with the latest available figures.

    The snapshot left-joins the authoritative company universe with the
    latest financial ratios and the latest market-cap data, so every
    company is present even when some tables have no rows for it
    (missing values stay NaN).

    Columns:
        company_id, company_name, broad_sector, industry,
        market_cap_category, ratio_year, <RATIO_FIELDS>,
        market_cap_year, market_cap, pe_ratio, pb_ratio, dividend_yield
    """
    companies = load_companies(db_path)
    validate_universe(companies)

    ratios = load_ratios_history(db_path)
    latest_ratios = _latest_rows(ratios)
    latest_ratios = latest_ratios.rename(columns={"calendar_year": "ratio_year"})

    market_cap = load_market_cap_history(db_path)
    latest_market = _latest_rows(market_cap)
    latest_market = latest_market.rename(
        columns={"calendar_year": "market_cap_year"}
    )

    snapshot = companies.merge(
        latest_ratios[
            ["company_id", "ratio_year"] + RATIO_FIELDS
        ],
        on="company_id",
        how="left",
    )
    snapshot = snapshot.merge(
        latest_market[
            [
                "company_id",
                "market_cap_year",
                "market_cap",
                "pe_ratio",
                "pb_ratio",
                "dividend_yield",
            ]
        ],
        on="company_id",
        how="left",
    )

    return snapshot
