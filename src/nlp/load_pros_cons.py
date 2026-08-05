from pathlib import Path
import sqlite3

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

DATABASE = ROOT / "nifty100.db"
CSV_FILE = ROOT / "output" / "pros_cons_generated.csv"


def main():

    conn = sqlite3.connect(DATABASE)

    try:

        df = pd.read_csv(CSV_FILE)

        # Build one row per company
        records = []

        for company_id, group in df.groupby("company_id"):

            pros = "\n".join(
                "✓ " + t
                for t in group.loc[group["type"] == "pro", "text"]
            )

            cons = "\n".join(
                "✗ " + t
                for t in group.loc[group["type"] == "con", "text"]
            )

            records.append(
                (
                    company_id,
                    pros,
                    cons,
                )
            )

        cur = conn.cursor()

        cur.execute("DELETE FROM prosandcons")

        cur.executemany(
            """
            INSERT INTO prosandcons
            (
                company_id,
                pros,
                cons
            )
            VALUES
            (?, ?, ?)
            """,
            records,
        )

        conn.commit()

        print(f"Loaded {len(records)} companies into prosandcons table.")

    finally:

        conn.close()


if __name__ == "__main__":
    main()