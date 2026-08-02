"""
Sprint 5 - Day 29
NLP Analysis Parser

Parses analysis.xlsx text fields into structured CAGR metrics.

Outputs:
    output/analysis_parsed.csv
    output/parse_failures.csv
    output/cagr_review.csv
"""

from __future__ import annotations

import logging
import re
import sqlite3
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ANALYSIS_FILE = PROJECT_ROOT / "data" / "raw" / "analysis.xlsx"
DATABASE_FILE = PROJECT_ROOT / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

PARSED_FILE = OUTPUT_DIR / "analysis_parsed.csv"
FAILURES_FILE = OUTPUT_DIR / "parse_failures.csv"
REVIEW_FILE = OUTPUT_DIR / "cagr_review.csv"

PATTERN = re.compile(
    r"(\d+)\s*Years?:?\s*(-?[\d.]+)%",
    flags=re.IGNORECASE,
)

TARGET_COLUMNS = {
    "compounded_sales_growth": "revenue_cagr",
    "compounded_profit_growth": "pat_cagr",
    "stock_price_cagr": "stock_price_cagr",
    "roe": "roe",
}


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def load_analysis() -> pd.DataFrame:
    logging.info("Loading analysis.xlsx")

    df = pd.read_excel(
        ANALYSIS_FILE,
        sheet_name="Analysis",
        header=1,
    )

    df.columns = [str(c).strip() for c in df.columns]

    return df


def parse_metric(
    text: object,
) -> Optional[Tuple[int, float]]:
    if pd.isna(text):
        return None

    text = str(text).strip()

    match = PATTERN.search(text)

    if not match:
        return None

    years = int(match.group(1))
    value = float(match.group(2))

    return years, value


def parse_dataframe(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    parsed_rows = []
    failed_rows = []

    for _, row in df.iterrows():

        company_id = row["company_id"]

        for column_name, metric_name in TARGET_COLUMNS.items():

            if column_name not in df.columns:
                continue

            value = row[column_name]

            result = parse_metric(value)

            if result is None:

                failed_rows.append(
                    {
                        "company_id": company_id,
                        "metric": metric_name,
                        "original_text": value,
                    }
                )

                continue

            period_years, value_pct = result

            parsed_rows.append(
                {
                    "company_id": company_id,
                    "metric_type": metric_name,
                    "period_years": period_years,
                    "value_pct": value_pct,
                }
            )

    parsed_df = pd.DataFrame(parsed_rows)
    failed_df = pd.DataFrame(failed_rows)

    return parsed_df, failed_df


def load_ratios() -> pd.DataFrame:
    logging.info("Loading financial_ratios")

    conn = sqlite3.connect(DATABASE_FILE)

    query = """
    SELECT
        company_id,
        revenue_cagr_5yr,
        pat_cagr_5yr
    FROM financial_ratios
    """

    ratios = pd.read_sql(query, conn)

    conn.close()

    return ratios


def cross_validate(
    parsed_df: pd.DataFrame,
    ratios_df: pd.DataFrame,
) -> pd.DataFrame:

    review_rows = []

    sales_df = parsed_df[
        (parsed_df["metric_type"] == "revenue_cagr")
        & (parsed_df["period_years"] == 5)
    ]

    profit_df = parsed_df[
        (parsed_df["metric_type"] == "pat_cagr")
        & (parsed_df["period_years"] == 5)
    ]

    sales_merge = sales_df.merge(
        ratios_df,
        on="company_id",
        how="left",
    )

    for _, row in sales_merge.iterrows():

        parsed_value = row["value_pct"]
        computed_value = row["revenue_cagr_5yr"]

        if pd.isna(computed_value):
            continue

        diff = abs(parsed_value - computed_value)

        if diff > 5:

            review_rows.append(
                {
                    "company_id": row["company_id"],
                    "metric": "revenue_cagr",
                    "parsed_value": parsed_value,
                    "computed_value": computed_value,
                    "difference": diff,
                }
            )

    profit_merge = profit_df.merge(
        ratios_df,
        on="company_id",
        how="left",
    )

    for _, row in profit_merge.iterrows():

        parsed_value = row["value_pct"]
        computed_value = row["pat_cagr_5yr"]

        if pd.isna(computed_value):
            continue

        diff = abs(parsed_value - computed_value)

        if diff > 5:

            review_rows.append(
                {
                    "company_id": row["company_id"],
                    "metric": "pat_cagr",
                    "parsed_value": parsed_value,
                    "computed_value": computed_value,
                    "difference": diff,
                }
            )

    return pd.DataFrame(review_rows)


def save_outputs(
    parsed_df: pd.DataFrame,
    failed_df: pd.DataFrame,
    review_df: pd.DataFrame,
) -> None:

    parsed_df.to_csv(
        PARSED_FILE,
        index=False,
    )

    failed_df.to_csv(
        FAILURES_FILE,
        index=False,
    )

    review_df.to_csv(
        REVIEW_FILE,
        index=False,
    )

    logging.info(
        "Saved %s",
        PARSED_FILE,
    )

    logging.info(
        "Saved %s",
        FAILURES_FILE,
    )

    logging.info(
        "Saved %s",
        REVIEW_FILE,
    )


def main() -> None:

    df = load_analysis()

    parsed_df, failed_df = parse_dataframe(df)

    ratios_df = load_ratios()

    review_df = cross_validate(
        parsed_df,
        ratios_df,
    )

    save_outputs(
        parsed_df,
        failed_df,
        review_df,
    )

    logging.info(
        "Parsed rows: %s",
        len(parsed_df),
    )

    logging.info(
        "Failures: %s",
        len(failed_df),
    )

    logging.info(
        "Review rows: %s",
        len(review_df),
    )


if __name__ == "__main__":
    main()