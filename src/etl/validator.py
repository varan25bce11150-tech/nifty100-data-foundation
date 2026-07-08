import sqlite3
import pandas as pd
from pathlib import Path

DATABASE = "nifty100.db"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

FAILURES = []


def add_failure(rule, severity, table, record, message):
    FAILURES.append({
        "rule": rule,
        "severity": severity,
        "table": table,
        "record": record,
        "message": message
    })


class DataValidator:

    def __init__(self, db_path):

        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

    def execute(self, query):

        self.cur.execute(query)
        return self.cur.fetchall()


    # --------------------------------------------------
    # DQ-01 Primary Key Duplicate
    # --------------------------------------------------

    def dq01_primary_key(self):

        tables = [
            "companies",
            "profitandloss",
            "balancesheet",
            "cashflow",
            "analysis",
            "documents",
            "financial_ratios",
            "market_cap",
            "peer_groups",
            "prosandcons",
            "sectors",
            "stock_prices"
        ]

        for table in tables:

            rows = self.execute(f"""

            SELECT id,
                   COUNT(*)

            FROM {table}

            GROUP BY id

            HAVING COUNT(*)>1

            """)

            for row in rows:

                add_failure(
                    "DQ-01",
                    "CRITICAL",
                    table,
                    row[0],
                    "Duplicate primary key"
                )


    # --------------------------------------------------
    # DQ-02 Duplicate company-year
    # --------------------------------------------------

    def dq02_company_year(self):

        tables = [
            "profitandloss",
            "balancesheet",
            "cashflow",
            "market_cap"
        ]

        for table in tables:

            rows = self.execute(f"""

            SELECT company_id,
                   year,
                   COUNT(*)

            FROM {table}

            GROUP BY company_id,year

            HAVING COUNT(*)>1

            """)

            for row in rows:

                add_failure(
                    "DQ-02",
                    "CRITICAL",
                    table,
                    f"{row[0]}-{row[1]}",
                    "Duplicate company/year"
                )


    # --------------------------------------------------
    # DQ-03 Foreign Keys
    # --------------------------------------------------

    def dq03_foreign_keys(self):

        rows = self.execute(

            "PRAGMA foreign_key_check"

        )

        for row in rows:

            add_failure(
                "DQ-03",
                "CRITICAL",
                row[0],
                row[1],
                "Foreign key violation"
            )


    # --------------------------------------------------
    # DQ-04 Positive Sales
    # --------------------------------------------------

    def dq04_sales(self):

        rows = self.execute("""

        SELECT id

        FROM profitandloss

        WHERE sales<=0

        """)

        for row in rows:

            add_failure(
                "DQ-04",
                "WARNING",
                "profitandloss",
                row[0],
                "Sales <= 0"
            )


    # --------------------------------------------------
    # DQ-05 Balance Sheet
    # --------------------------------------------------

    def dq05_balance(self):

        rows = self.execute("""

        SELECT id

        FROM balancesheet

        WHERE ABS(
            total_assets-total_liabilities
        )>1

        """)

        for row in rows:

            add_failure(
                "DQ-05",
                "WARNING",
                "balancesheet",
                row[0],
                "Assets and liabilities mismatch"
            )