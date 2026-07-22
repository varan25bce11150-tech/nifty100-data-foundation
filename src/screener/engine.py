"""
Sprint 3 - Day 15
Financial Screener Engine
"""

import sqlite3
from pathlib import Path

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "nifty100.db"
CONFIG_PATH = PROJECT_ROOT / "config" / "screener_config.yaml"


class ScreenerEngine:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)

    def load_config(self):
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)

    def load_data(self):

        query = """
        SELECT

            c.company_name,

            fr.company_id,
            fr.year,

            fr.return_on_equity_pct,
            fr.return_on_capital_employed_pct,
            fr.net_profit_margin_pct,
            fr.operating_profit_margin_pct,

            fr.debt_to_equity,
            fr.interest_coverage,
            fr.icr_label,

            fr.asset_turnover,

            fr.free_cash_flow_cr,

            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            fr.eps_cagr_5yr,

            fr.composite_quality_score,

            mc.market_cap,
            mc.pe_ratio,
            mc.pb_ratio,
            mc.dividend_yield,

            pl.sales,
            pl.net_profit,
            pl.dividend_payout,

            pg.sector

        FROM financial_ratios fr

        LEFT JOIN companies c
            ON fr.company_id = c.id

        LEFT JOIN market_cap mc
            ON fr.company_id = mc.company_id
            AND fr.year = mc.year

        LEFT JOIN profitandloss pl
            ON fr.company_id = pl.company_id
            AND fr.year = CAST(SUBSTR(pl.year, -4) AS INTEGER)

        LEFT JOIN peer_groups pg
            ON fr.company_id = pg.company
        """

        df = pd.read_sql(query, self.conn)

        # Debt Free => Infinite Interest Coverage
        df.loc[
            df["icr_label"].fillna("").str.lower() == "debt free",
            "interest_coverage",
        ] = float("inf")

        # ============================================================
        # Keep only the latest financial year for each company
        # ============================================================
        df = (
            df.sort_values("year")
              .groupby("company_id", as_index=False)
              .tail(1)
              .reset_index(drop=True)
        )

        return df

    def apply_filters(self, df, filters):

        result = df.copy()

        metric_map = {

            "return_on_equity_pct_min":
                ("return_on_equity_pct", ">="),

            "return_on_capital_employed_pct_min":
                ("return_on_capital_employed_pct", ">="),

            "net_profit_margin_pct_min":
                ("net_profit_margin_pct", ">="),

            "operating_profit_margin_pct_min":
                ("operating_profit_margin_pct", ">="),

            "debt_to_equity_max":
                ("debt_to_equity", "<="),

            "interest_coverage_min":
                ("interest_coverage", ">="),

            "free_cash_flow_cr_min":
                ("free_cash_flow_cr", ">="),

            "revenue_cagr_5yr_min":
                ("revenue_cagr_5yr", ">="),

            "pat_cagr_5yr_min":
                ("pat_cagr_5yr", ">="),

            "eps_cagr_5yr_min":
                ("eps_cagr_5yr", ">="),

            "asset_turnover_min":
                ("asset_turnover", ">="),

            "market_cap_min":
                ("market_cap", ">="),

            "sales_min":
                ("sales", ">="),

            "net_profit_min":
                ("net_profit", ">="),

            "pe_ratio_max":
                ("pe_ratio", "<="),

            "pb_ratio_max":
                ("pb_ratio", "<="),

            "dividend_yield_min":
                ("dividend_yield", ">="),

            "dividend_payout_max":
                ("dividend_payout", "<="),
        }

        for key, value in filters.items():

            if key not in metric_map:
                continue

            column, operator = metric_map[key]

            if column not in result.columns:
                continue

            if column == "debt_to_equity":

                financial = result["sector"].fillna("").str.contains(
                    "bank|financial|insurance",
                    case=False,
                    regex=True,
                )

                if operator == "<=":
                    result = result[
                        financial |
                        (result[column].fillna(9999) <= value)
                    ]

                continue

            if operator == ">=":
                result = result[result[column].fillna(-999999) >= value]

            else:
                result = result[result[column].fillna(999999) <= value]

        return result.sort_values(
            by="composite_quality_score",
            ascending=False,
        )

    def run_preset(self, preset_name):

        config = self.load_config()

        if preset_name not in config:
            raise ValueError(f"Preset '{preset_name}' not found.")

        df = self.load_data()

        return self.apply_filters(
            df,
            config[preset_name],
        )


if __name__ == "__main__":

    engine = ScreenerEngine()

    df = engine.run_preset("quality_compounder")

    print(df.head())

    print()

    print("Companies found:", len(df))