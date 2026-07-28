"""
Sprint 2 - Financial Ratio Engine

Reads data from SQLite
Calculates KPIs
Stores results in financial_ratios
"""

import sqlite3

from src.analytics.db_loader import DatabaseLoader

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    interest_coverage_ratio,
    interest_coverage_label,
    asset_turnover,
)

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    capex_intensity,
    fcf_conversion_rate,
)

from src.analytics.cagr import (
    revenue_cagr_5yr,
    pat_cagr_5yr,
    eps_cagr_5yr,
)


class RatioEngine:

    def __init__(self, db_path="nifty100.db"):

        self.db = DatabaseLoader(db_path)

        self.conn = sqlite3.connect(db_path)

        self.cursor = self.conn.cursor()

    # ------------------------------------------

    def load(self):

        self.pnl = self.db.fetch_profit_and_loss()

        self.bs = self.db.fetch_balance_sheet()

        self.cf = self.db.fetch_cashflow()

        self.companies = self.db.fetch_companies()

        self.sectors = self.db.fetch_sectors()

    # ------------------------------------------

    def common_keys(self):

        return sorted(

            set(self.pnl.keys())

            &

            set(self.bs.keys())

        )
    
    # ------------------------------------------

    def calculate_ratios(
        self,
        company,
        year,
        pnl,
        bs,
        cf=None,
        old_pnl=None,
    ):
        sales = pnl["sales"]
        operating_profit = pnl["operating_profit"]
        other_income = pnl["other_income"]
        interest = pnl["interest"]
        net_profit = pnl["net_profit"]
        eps = pnl["eps"]

        equity = bs["equity_capital"]
        reserves = bs["reserves"]
        borrowings = bs["borrowings"]
        investments = bs["investments"]
        total_assets = bs["total_assets"]

        ratios = {}

        ratios["company_id"] = company
        ratios["year"] = year

        # ---------------- Profitability ----------------

        ratios["net_profit_margin_pct"] = net_profit_margin(
            net_profit,
            sales,
        )

        ratios["operating_profit_margin_pct"] = operating_profit_margin(
            operating_profit,
            sales,
        )

        ratios["return_on_equity_pct"] = return_on_equity(
            net_profit,
            equity,
            reserves,
        )

        ratios["return_on_capital_employed_pct"] = (
            return_on_capital_employed(
                operating_profit,
                other_income,
                equity,
                reserves,
                borrowings,
            )
        )

        ratios["return_on_assets_pct"] = (
            return_on_assets(
                net_profit,
                total_assets,
            )
        )

        # ---------------- Leverage ----------------

        ratios["debt_to_equity"] = debt_to_equity(
            borrowings,
            equity,
            reserves,
        )

        icr = interest_coverage_ratio(
            operating_profit,
            other_income,
            interest,
        )

        ratios["interest_coverage"] = icr

        ratios["icr_label"] = interest_coverage_label(icr)

        ratios["asset_turnover"] = asset_turnover(
            sales,
            total_assets,
        )

        # ---------------- Cash Flow ----------------

        if cf:

            ratios["free_cash_flow_cr"] = free_cash_flow(
                cf["operating_activity"],
                cf["investing_activity"],
            )

            ratios["capex_intensity_pct"] = capex_intensity(
                cf["investing_activity"],
                sales,
            )

            ratios["fcf_conversion_pct"] = (
                fcf_conversion_rate(
                    cf["operating_activity"],
                    cf["investing_activity"],
                    operating_profit,
                )
            )

        else:

            ratios["free_cash_flow_cr"] = None
            ratios["capex_intensity_pct"] = None
            ratios["fcf_conversion_pct"] = None
    # ---------------- CAGR ----------------

    if old_pnl:

        revenue, revenue_flag = revenue_cagr_5yr(
            old_pnl["sales"],
            sales,
        )

        pat, pat_flag = pat_cagr_5yr(
            old_pnl["net_profit"],
            net_profit,
        )

        eps_value, eps_flag = eps_cagr_5yr(
            old_pnl["eps"],
            eps,
        )

        ratios["revenue_cagr_5yr"] = revenue
        ratios["revenue_cagr_5yr_flag"] = revenue_flag.value

        ratios["pat_cagr_5yr"] = pat
        ratios["pat_cagr_5yr_flag"] = pat_flag.value

        ratios["eps_cagr_5yr"] = eps_value
        ratios["eps_cagr_5yr_flag"] = eps_flag.value

    else:

        ratios["revenue_cagr_5yr"] = None
        ratios["revenue_cagr_5yr_flag"] = "INSUFFICIENT"

        ratios["pat_cagr_5yr"] = None
        ratios["pat_cagr_5yr_flag"] = "INSUFFICIENT"

        ratios["eps_cagr_5yr"] = None
        ratios["eps_cagr_5yr_flag"] = "INSUFFICIENT"      

     # ---------------- Composite Score ----------------

        score = 0

        for value in [

            ratios["return_on_equity_pct"],
            ratios["return_on_assets_pct"],
            ratios["net_profit_margin_pct"],
            ratios["operating_profit_margin_pct"]

        ]:

            if value is not None:
                score += value

        ratios["composite_quality_score"] = round(
            score,
            2,
        )

        return ratios


    # --------------------------------------------------
    # Insert one ratio record into SQLite
    # --------------------------------------------------

    def insert_ratio(self, r):

        self.cursor.execute(
            """
            INSERT INTO financial_ratios(

                company_id,
                year,

                net_profit_margin_pct,
                operating_profit_margin_pct,

                return_on_equity_pct,
                return_on_capital_employed_pct,
                return_on_assets_pct,

                debt_to_equity,
                interest_coverage,
                icr_label,

                asset_turnover,

                free_cash_flow_cr,
                capex_intensity_pct,
                fcf_conversion_pct,

                revenue_cagr_5yr,
                revenue_cagr_5yr_flag,

                pat_cagr_5yr,
                pat_cagr_5yr_flag,

                eps_cagr_5yr,
                eps_cagr_5yr_flag,

                composite_quality_score

            )

            VALUES(
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
)
            """,

            (

                r["company_id"],
                r["year"],

                r["net_profit_margin_pct"],
                r["operating_profit_margin_pct"],

                r["return_on_equity_pct"],
                r["return_on_capital_employed_pct"],

                r["return_on_assets_pct"],

                r["debt_to_equity"],
                r["interest_coverage"],
                r["icr_label"],

                r["asset_turnover"],

                r["free_cash_flow_cr"],
                r["capex_intensity_pct"],
                r["fcf_conversion_pct"],

                r["revenue_cagr_5yr"],
                r["revenue_cagr_5yr_flag"],

                r["pat_cagr_5yr"],
                r["pat_cagr_5yr_flag"],

                r["eps_cagr_5yr"],
                r["eps_cagr_5yr_flag"],

                r["composite_quality_score"]

            )

        )

    # --------------------------------------------------
    # Run Engine
    # --------------------------------------------------

    def run(self):

        print("Loading data...")

        self.load()

        print("Clearing financial_ratios table...")

        self.cursor.execute(
            "DELETE FROM financial_ratios"
        )

        keys = self.common_keys()

        inserted = 0

        for company, year in keys:

            pnl = self.pnl[(company, year)]

            bs = self.bs[(company, year)]

            cf = self.cf.get((company, year))

            # Get financial data from 5 years earlier
            old_pnl = self.pnl.get((company, year - 5))

            ratios = self.calculate_ratios(

                company,
                year,
                pnl,
                bs,
                cf,
                old_pnl,

            )

            self.insert_ratio(ratios)

            inserted += 1

        self.conn.commit()

        print(f"\nInserted {inserted} rows.")

        self.db.close()

        self.conn.close()


if __name__ == "__main__":

    engine = RatioEngine()

    engine.run()            