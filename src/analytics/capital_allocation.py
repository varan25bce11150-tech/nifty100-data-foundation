"""
Sprint 2 - Day 11
Capital Allocation Pattern Generator

Creates:
output/capital_allocation.csv
"""

import os
import sqlite3
import pandas as pd

DB_PATH = "nifty100.db"
OUTPUT_FILE = "output/capital_allocation.csv"


def sign(value):
    if value is None:
        return "0"
    if value > 0:
        return "+"
    if value < 0:
        return "-"
    return "0"


def classify(cfo, cfi, cff):

    pattern = (cfo, cfi, cff)

    if pattern == ("+", "-", "-"):
        return "Reinvestor"

    elif pattern == ("+", "+", "-"):
        return "Liquidating Assets"

    elif pattern == ("-", "+", "+"):
        return "Distress Signal"

    elif pattern == ("-", "-", "+"):
        return "Growth Funded by Debt"

    elif pattern == ("+", "+", "+"):
        return "Cash Accumulator"

    elif pattern == ("-", "-", "-"):
        return "Pre-Revenue"

    elif pattern == ("+", "-", "+"):
        return "Mixed"

    else:
        return "Other"


def main():

    os.makedirs("output", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        company_id,
        year,
        operating_activity,
        investing_activity,
        financing_activity
    FROM cashflow
    """

    df = pd.read_sql(query, conn)

    df["cfo_sign"] = df["operating_activity"].apply(sign)
    df["cfi_sign"] = df["investing_activity"].apply(sign)
    df["cff_sign"] = df["financing_activity"].apply(sign)

    df["pattern_label"] = df.apply(
        lambda r: classify(
            r["cfo_sign"],
            r["cfi_sign"],
            r["cff_sign"],
        ),
        axis=1,
    )

    output = df[
        [
            "company_id",
            "year",
            "cfo_sign",
            "cfi_sign",
            "cff_sign",
            "pattern_label",
        ]
    ]

    output.to_csv(OUTPUT_FILE, index=False)

    print("=" * 50)
    print("Capital Allocation Report Generated")
    print(f"Rows : {len(output)}")
    print(f"Saved: {OUTPUT_FILE}")
    print("=" * 50)

    conn.close()


if __name__ == "__main__":
    main()