"""
Sprint 5
Pros & Cons Generator

Runs all NLP rules against every company and generates:

output/pros_cons_generated.csv
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

import pandas as pd

from src.nlp.rules import (
    PRO_RULES,
    CON_RULES,
)

# -------------------------------------------------------
# Paths
# -------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

DATABASE = ROOT / "nifty100.db"

OUTPUT = ROOT / "output"

OUTPUT.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT / "pros_cons_generated.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------
# Database
# -------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    """
    Create SQLite connection.
    """

    return sqlite3.connect(DATABASE)


# -------------------------------------------------------
# Load Tables
# -------------------------------------------------------

def load_companies(conn):

    return pd.read_sql(
        """
        SELECT *
        FROM companies
        ORDER BY id
        """,
        conn,
    )


def load_ratios(conn, company):

    return pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[company],
    )


def load_profit(conn, company):

    return pd.read_sql(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[company],
    )


def load_balance(conn, company):

    return pd.read_sql(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[company],
    )


def load_cashflow(conn, company):

    return pd.read_sql(
        """
        SELECT *
        FROM cashflow
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[company],
    )


def load_market(conn, company):

    return pd.read_sql(
        """
        SELECT *
        FROM market_cap
        WHERE company_id=?
        ORDER BY year
        """,
        conn,
        params=[company],
    )


# -------------------------------------------------------
# Build Company Context
# -------------------------------------------------------

def company_context(conn, company):

    return {

        "ratios": load_ratios(conn, company),

        "profit": load_profit(conn, company),

        "balance": load_balance(conn, company),

        "cashflow": load_cashflow(conn, company),

        "market": load_market(conn, company),
    }

# -------------------------------------------------------
# Execute Rules
# -------------------------------------------------------

def execute_pro_rules(context: dict):

    results = []

    ratios = context["ratios"]
    market = context["market"]

    for rule in PRO_RULES:

        try:

            # Rule 8 uses ratios + market
            if rule.__name__ == "rule_pro_08":

                result = rule(
                    ratios,
                    market,
                )

            # Rule 12 uses balance sheet
            elif rule.__name__ == "rule_pro_12":

                result = rule(
                    context["balance"],
                )

            else:

                result = rule(
                    ratios,
                )

            if result is not None:

                results.append(result)

        except Exception as e:

            logger.exception(
                "%s failed",
                rule.__name__,
            )

    return results


def execute_con_rules(context: dict):

    results = []

    ratios = context["ratios"]

    for rule in CON_RULES:

        try:

            name = rule.__name__

            if name in [
                "rule_con_04",
                "rule_con_05",
                "rule_con_07",
                "rule_con_09",
            ]:

                result = rule(
                    context["profit"],
                )

            elif name == "rule_con_11":

                result = rule(
                    context["balance"],
                )

            else:

                result = rule(
                    ratios,
                )

            if result is not None:

                results.append(result)

        except Exception:

            logger.exception(
                "%s failed",
                rule.__name__,
            )

    return results


# -------------------------------------------------------
# Run Company
# -------------------------------------------------------

def analyse_company(
    conn,
    company_id,
):

    context = company_context(
        conn,
        company_id,
    )

    pros = execute_pro_rules(
        context,
    )

    cons = execute_con_rules(
        context,
    )

    return pros + cons

# -------------------------------------------------------
# Build Output
# -------------------------------------------------------

def build_output(conn) -> pd.DataFrame:
    """
    Execute all rules for all companies and build
    the final Pros/Cons dataframe.
    """

    companies = load_companies(conn)

    records = []

    logger.info(
        "Processing %d companies...",
        len(companies),
    )

    for _, company in companies.iterrows():

        company_id = company["id"]

        logger.info(
            "Running rules for %s",
            company_id,
        )

        try:

            results = analyse_company(
                conn,
                company_id,
            )

            # --------------------------------------------------
            # Normalize rule outputs
            # Supports dict and object formats
            # --------------------------------------------------

            cleaned_results = []

            for r in results:

                if r is None:
                    continue

                if isinstance(r, dict):

                    confidence = r.get(
                        "confidence",
                        r.get("confidence_pct", 0),
                    )

                else:

                     confidence = getattr(
                         r,
                         "confidence_pct",
                         0,
                     )


                if confidence > 60:
                    cleaned_results.append(r)


            results = cleaned_results


            # --------------------------------------------------
            # Extract helper
            # --------------------------------------------------

            def get_value(item, key):

                if isinstance(item, dict):
                    return item.get(key)

                return getattr(
                    item,
                    key,
                    None,
                )


            # --------------------------------------------------
            # Guarantee PRO
            # --------------------------------------------------

            if not any(
                get_value(r, "type") == "pro"
                for r in results
            ):

                results.append(
                    {
                        "rule_id": "AUTO_PRO",
                        "type": "pro",
                        "text": (
                            "Business exhibits at least one "
                            "positive financial characteristic "
                            "requiring further review."
                        ),
                        "confidence_pct": 61,
                    }
                )


            # --------------------------------------------------
            # Guarantee CON
            # --------------------------------------------------

            if not any(
                get_value(r, "type") == "con"
                for r in results
            ):

                results.append(
                    {
                        "rule_id": "AUTO_CON",
                        "type": "con",
                        "text": (
                            "No major financial weakness detected "
                            "by automated screening, though "
                            "periodic monitoring is recommended."
                        ),
                        "confidence_pct": 61,
                    }
                )


            # --------------------------------------------------
            # Convert everything into dataframe records
            # --------------------------------------------------

            for r in results:

                records.append(
                    {
                        "company_id": company_id,
                        "type": get_value(r, "type"),
                        "rule_id": get_value(r, "rule_id"),
                        "text": get_value(r, "text"),
                        "confidence_pct": (
                            get_value(r, "confidence")
                            if get_value(r, "confidence") is not None
                            else get_value(r, "confidence_pct")
                         ),
                    }
                )


        except Exception:

            logger.exception(
                "Failed processing %s",
                company_id,
            )


    return pd.DataFrame(records)            

# -------------------------------------------------------
# Save
# -------------------------------------------------------

def save_output(df: pd.DataFrame):

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    logger.info(
        "Saved %d records -> %s",
        len(df),
        OUTPUT_FILE,
    )


# -------------------------------------------------------
# Main
# -------------------------------------------------------

def main():

    logger.info(
        "Starting Pros & Cons Generator..."
    )

    conn = get_connection()

    try:

        df = build_output(conn)

        save_output(df)

        logger.info(
            "Generation Complete."
        )

    finally:

        conn.close()


if __name__ == "__main__":

    main()