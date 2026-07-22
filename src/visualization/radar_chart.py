"""
Sprint 3 - Day 17
Bulk Radar Chart Generator
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output" / "radar_charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class RadarChartGenerator:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)


    def load_data(self):

        query = """
        SELECT
            c.company_name,

            fr.return_on_equity_pct,
            fr.return_on_capital_employed_pct,
            fr.net_profit_margin_pct,
            fr.operating_profit_margin_pct,
            fr.asset_turnover,

            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,

            fr.composite_quality_score

        FROM financial_ratios fr

        JOIN companies c
            ON fr.company_id = c.id

        WHERE fr.year = (
            SELECT MAX(year)
            FROM financial_ratios
        )
        """

        return pd.read_sql(query, self.conn)


    def clean_filename(self, name):

        return (
            name
            .replace("\n", " ")
            .replace("/", "_")
            .replace("\\", "_")
            .replace(" ", "_")
        )


    def create_chart(self, row):

        company = row["company_name"]

        labels = [
            "ROE",
            "ROCE",
            "NPM",
            "OPM",
            "Asset Turnover",
            "Revenue CAGR",
            "PAT CAGR",
            "Quality Score",
        ]


        values = [
            row["return_on_equity_pct"],
            row["return_on_capital_employed_pct"],
            row["net_profit_margin_pct"],
            row["operating_profit_margin_pct"],
            row["asset_turnover"],
            row["revenue_cagr_5yr"],
            row["pat_cagr_5yr"],
            row["composite_quality_score"],
        ]


        values = [
            0 if pd.isna(v) else float(v)
            for v in values
        ]


        values += values[:1]


        angles = np.linspace(
            0,
            2*np.pi,
            len(labels),
            endpoint=False
        ).tolist()

        angles += angles[:1]


        fig = plt.figure(figsize=(7,7))

        ax = plt.subplot(
            111,
            polar=True
        )


        ax.plot(
            angles,
            values,
            linewidth=2
        )

        ax.fill(
            angles,
            values,
            alpha=0.25
        )


        ax.set_xticks(
            angles[:-1]
        )

        ax.set_xticklabels(
            labels
        )


        plt.title(
            company.replace("\n"," "),
            fontsize=12
        )


        filename = (
            OUTPUT_DIR /
            f"{self.clean_filename(company)}.png"
        )


        plt.savefig(
            filename,
            dpi=300,
            bbox_inches="tight"
        )


        plt.close()


    def run(self):

        df = self.load_data()


        count = 0


        for _, row in df.iterrows():

            self.create_chart(row)

            count += 1

            print(
                f"Generated: {row['company_name']}"
            )


        print()
        print(
            f"Total radar charts created: {count}"
        )


if __name__ == "__main__":

    RadarChartGenerator().run()