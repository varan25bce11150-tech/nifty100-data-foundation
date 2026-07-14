"""
Database Loader
Loads yearly financial data from SQLite
"""

import sqlite3
from src.analytics.year_utils import extract_year


class DatabaseLoader:

    def __init__(self, db_path="nifty100.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def fetch_profit_and_loss(self):

        query = """
        SELECT *
        FROM profitandloss
        """

        rows = self.conn.execute(query).fetchall()

        data = {}

        for row in rows:

            company = row["company_id"]
            year = extract_year(row["year"])

            data[(company, year)] = dict(row)

        return data

    def fetch_balance_sheet(self):

        query = """
        SELECT *
        FROM balancesheet
        """

        rows = self.conn.execute(query).fetchall()

        data = {}

        for row in rows:

            company = row["company_id"]
            year = extract_year(row["year"])

            data[(company, year)] = dict(row)

        return data

    def fetch_cashflow(self):

        query = """
        SELECT *
        FROM cashflow
        """

        rows = self.conn.execute(query).fetchall()

        data = {}

        for row in rows:

            company = row["company_id"]
            year = extract_year(row["year"])

            data[(company, year)] = dict(row)

        return data

    def fetch_companies(self):

        rows = self.conn.execute(
            "SELECT * FROM companies"
        ).fetchall()

        return {
            row["id"]: dict(row)
            for row in rows
        }

    def fetch_sectors(self):

        rows = self.conn.execute(
            "SELECT * FROM sectors"
        ).fetchall()

        return {
            row["company_id"]: dict(row)
            for row in rows
        }

    def close(self):
        self.conn.close()