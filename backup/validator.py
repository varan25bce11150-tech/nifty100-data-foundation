import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("db/nifty100.db")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def add(rule, severity, table, message, results):
    results.append({
        "rule": rule,
        "severity": severity,
        "table": table,
        "message": message
    })


def run_validation():

    conn = sqlite3.connect(DB_PATH)

    results = []

    # ---------------------------------------
    # DQ-01 Duplicate Company IDs
    # ---------------------------------------
    df = pd.read_sql("""
        SELECT id,COUNT(*) cnt
        FROM companies
        GROUP BY id
        HAVING cnt>1
    """, conn)

    for _, r in df.iterrows():
        add(
            "DQ-01",
            "CRITICAL",
            "companies",
            f"Duplicate id {r['id']}",
            results
        )

    # ---------------------------------------
    # DQ-02 Duplicate Profit & Loss Keys
    # ---------------------------------------
    df = pd.read_sql("""
        SELECT company_id,year,COUNT(*) cnt
        FROM profitandloss
        GROUP BY company_id,year
        HAVING cnt>1
    """, conn)

    for _, r in df.iterrows():
        add(
            "DQ-02",
            "CRITICAL",
            "profitandloss",
            f"Duplicate ({r['company_id']},{r['year']})",
            results
        )

    # ---------------------------------------
    # DQ-03 Foreign Key Integrity
    # ---------------------------------------
    tables = [
        "profitandloss",
        "balancesheet",
        "cashflow",
        "analysis",
        "documents",
        "prosandcons",
        "financial_ratios",
        "market_cap",
        "peer_groups",
        "sectors",
        "stock_prices"
    ]

    for table in tables:

        query = f"""
        SELECT company_id
        FROM {table}
        WHERE company_id NOT IN (
            SELECT id FROM companies
        )
        """

        bad = pd.read_sql(query, conn)

        if len(bad):

            add(
                "DQ-03",
                "CRITICAL",
                table,
                f"{len(bad)} orphan company_id values",
                results
            )

    # ---------------------------------------
    # DQ-04 Positive Sales
    # ---------------------------------------

    bad = pd.read_sql("""
        SELECT *
        FROM profitandloss
        WHERE sales<=0
    """, conn)

    if len(bad):

        add(
            "DQ-04",
            "WARNING",
            "profitandloss",
            f"{len(bad)} rows have sales <=0",
            results
        )

    # ---------------------------------------
    # DQ-05 Balance Sheet Equation
    # ---------------------------------------

    bad = pd.read_sql("""
        SELECT *
        FROM balancesheet
        WHERE ABS(
            total_assets-total_liabilities
        )>1
    """, conn)

    if len(bad):

        add(
            "DQ-05",
            "WARNING",
            "balancesheet",
            f"{len(bad)} balance mismatches",
            results
        )

    report = pd.DataFrame(results)

    report.to_csv(
        OUTPUT_DIR/"validation_failures.csv",
        index=False
    )

    print(report)

    conn.close()


if __name__ == "__main__":
    run_validation()