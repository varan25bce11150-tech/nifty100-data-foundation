"""
Sprint 3 - Day 18
Peer Percentile Ranking Engine
"""

import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "nifty100.db"


class PeerEngine:

    METRICS = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "pat_cagr_5yr",
        "revenue_cagr_5yr",
        "eps_cagr_5yr",
        "interest_coverage",
        "asset_turnover",
    ]

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)

    def load(self):
        self.ratios = pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )

        self.peers = pd.read_sql(
            "SELECT * FROM peer_groups",
            self.conn
        )
    def create_table(self):

        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS peer_percentiles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company_id TEXT,

            peer_group_name TEXT,

            metric TEXT,

            value REAL,

            percentile_rank REAL,

            year INTEGER

        )
        """)

        cursor.execute("DELETE FROM peer_percentiles")

        self.conn.commit()


    def calculate_percentile(self, df, metric):

        temp = df[["company_id", "year", metric]].copy()

        temp = temp.dropna(subset=[metric])

        if temp.empty:
            return pd.DataFrame()

        ascending = metric != "debt_to_equity"

        temp["percentile_rank"] = (
            temp[metric]
            .rank(method="average", pct=True, ascending=ascending)
            * 100
        )

        if metric == "debt_to_equity":
            temp["percentile_rank"] = 100 - temp["percentile_rank"]

        temp["metric"] = metric

        temp.rename(columns={metric: "value"}, inplace=True)

        return temp
    def run(self):

        self.load()
        self.create_table()

        cursor = self.conn.cursor()

        groups = self.peers.groupby("sector")

        inserted = 0

        for group_name, peer_df in groups:

            companies = peer_df["company"].tolist()

            ratios = self.ratios[
                self.ratios["company_id"].isin(companies)
            ].copy()

            if ratios.empty:
                print(f"{group_name}: No data found")
                continue

            for metric in self.METRICS:

                ranked = self.calculate_percentile(ratios, metric)

                if ranked.empty:
                    continue

                for _, row in ranked.iterrows():

                    cursor.execute(
                        """
                        INSERT INTO peer_percentiles
                        (
                            company_id,
                            peer_group_name,
                            metric,
                            value,
                            percentile_rank,
                            year
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row["company_id"],
                            group_name,
                            row["metric"],
                            float(row["value"]) if pd.notna(row["value"]) else None,
                            round(float(row["percentile_rank"]), 2),
                            int(row["year"]),
                        ),
                    )

                    inserted += 1

        self.conn.commit()

        print("=" * 60)
        print("SPRINT 3 - DAY 18")
        print("=" * 60)
        print(f"Inserted {inserted} peer percentile records.")
        print("=" * 60)


if __name__ == "__main__":
    PeerEngine().run()