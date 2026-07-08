import sqlite3
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
DB_PATH = Path("db/nifty100.db")
OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(exist_ok=True)

FILES = {
    "companies.xlsx": "companies",
    "profitandloss.xlsx": "profitandloss",
    "balancesheet.xlsx": "balancesheet",
    "cashflow.xlsx": "cashflow",
    "analysis.xlsx": "analysis",
    "documents.xlsx": "documents",
    "prosandcons.xlsx": "prosandcons",
    "financial_ratios.xlsx": "financial_ratios",
    "market_cap.xlsx": "market_cap",
    "peer_groups.xlsx": "peer_groups",
    "sectors.xlsx": "sectors",
    "stock_prices.xlsx": "stock_prices"
}


def load_file(path):
    """
    Read excel.
    Skip title row if necessary.
    """

    if path.name in [
        "companies.xlsx",
        "profitandloss.xlsx",
        "balancesheet.xlsx",
        "cashflow.xlsx",
        "analysis.xlsx",
        "documents.xlsx",
        "prosandcons.xlsx"
    ]:
        return pd.read_excel(path, skiprows=1)

    return pd.read_excel(path)


def main():

    conn = sqlite3.connect(DB_PATH)

    audit = []

    for excel, table in FILES.items():

        print(f"Loading {excel}")

        df = load_file(RAW_DIR / excel)

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        df.to_sql(
            table,
            conn,
            if_exists="replace",
            index=False
        )

        audit.append({
            "table": table,
            "rows_loaded": len(df),
            "rejected": 0
        })

        print(f"{table} -> {len(df)} rows")

    pd.DataFrame(audit).to_csv(
        OUTPUT_DIR / "load_audit.csv",
        index=False
    )

    conn.close()

    print("\nDONE")


if __name__ == "__main__":
    main()