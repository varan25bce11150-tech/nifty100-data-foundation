"""
Sprint 2 - Day 13
Ratio Validator

Compares computed ROE and ROCE against
source values from companies table.

Logs anomalies to:
output/ratio_edge_cases.log
"""

import os
import sqlite3


DB_PATH = "nifty100.db"
OUTPUT_DIR = "output"
LOG_FILE = os.path.join(OUTPUT_DIR, "ratio_edge_cases.log")


def category(diff):
    if diff > 20:
        return "DATA SOURCE ISSUE"
    elif diff > 5:
        return "FORMULA DISCREPANCY"
    else:
        return "VERSION DIFFERENCE"


def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    rows = cur.execute("""
        SELECT
            fr.company_id,
            fr.year,

            fr.return_on_equity_pct,
            fr.return_on_capital_employed_pct,

            c.roe_percentage,
            c.roce_percentage

        FROM financial_ratios fr

        JOIN companies c
            ON fr.company_id = c.id
    """).fetchall()

    anomalies = 0

    with open(LOG_FILE, "w", encoding="utf-8") as f:

        f.write("=" * 60 + "\n")
        f.write("RATIO EDGE CASES\n")
        f.write("=" * 60 + "\n\n")

        for row in rows:

            company = row["company_id"]
            year = row["year"]

            # ---------- ROE ----------

            comp = row["return_on_equity_pct"]
            src = row["roe_percentage"]

            if comp is not None and src is not None:

                diff = abs(comp - src)

                if diff > 5:

                    anomalies += 1

                    f.write("[ROE]\n")
                    f.write(f"Company    : {company}\n")
                    f.write(f"Year       : {year}\n")
                    f.write(f"Computed   : {comp:.2f}\n")
                    f.write(f"Source     : {src:.2f}\n")
                    f.write(f"Difference : {diff:.2f}\n")
                    f.write(f"Category   : {category(diff)}\n")
                    f.write("-" * 60 + "\n\n")

            # ---------- ROCE ----------

            comp = row["return_on_capital_employed_pct"]
            src = row["roce_percentage"]

            if comp is not None and src is not None:

                diff = abs(comp - src)

                if diff > 5:

                    anomalies += 1

                    f.write("[ROCE]\n")
                    f.write(f"Company    : {company}\n")
                    f.write(f"Year       : {year}\n")
                    f.write(f"Computed   : {comp:.2f}\n")
                    f.write(f"Source     : {src:.2f}\n")
                    f.write(f"Difference : {diff:.2f}\n")
                    f.write(f"Category   : {category(diff)}\n")
                    f.write("-" * 60 + "\n\n")

    conn.close()

    print("=" * 50)
    print("Ratio validation completed")
    print(f"Anomalies found : {anomalies}")
    print(f"Saved log       : {LOG_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    main()