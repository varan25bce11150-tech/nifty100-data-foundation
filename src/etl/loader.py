import pandas as pd
import sqlite3
import os
import traceback


DATABASE = "nifty100.db"
RAW_PATH = "data/raw"


# Files where first row contains headers
HEADER_ZERO_FILES = [
    "stock_prices.xlsx",
    "financial_ratios.xlsx",
    "peer_groups.xlsx",
    "sectors.xlsx",
    "market_cap.xlsx"
]

def load_excel(file):

    path = os.path.join(
        RAW_PATH,
        file
    )


    # Special formatting files
    if file in HEADER_ZERO_FILES:

        df = pd.read_excel(
            path,
            header=0
        )

    else:

        df = pd.read_excel(
            path,
            header=1
        )


    # Remove completely empty columns
    df = df.dropna(
        axis=1,
        how="all"
    )


    # Remove completely empty rows
    df = df.dropna(
        axis=0,
        how="all"
    )


    return df



def clean_columns(df):

    df.columns = [
        str(col)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace(".", "_")
        for col in df.columns
    ]


    return df



def fix_special_tables(df, table):

    """
    Fix files where Excel headers are inconsistent
    """


    # Financial ratios
    if table == "financial_ratios":

        df.columns = [
            "id",
            "company_id",
            "period",
            "ratio1",
            "ratio2",
            "ratio3",
            "ratio4",
            "ratio5",
            "ratio6",
            "ratio7",
            "ratio8",
            "ratio9",
            "ratio10",
            "ratio11",
            "ratio12",
            "ratio13"
        ][:len(df.columns)]


    # Peer groups

    elif table == "peer_groups":

        df.columns = [
            "id",
            "sector",
            "company",
            "is_peer"
        ][:len(df.columns)]


    # Sectors

    elif table == "sectors":

        df.columns = [
            "id",
            "company_id",
            "sector",
            "industry",
            "ratio",
            "market_cap_category"
        ][:len(df.columns)]
    # Market cap

    if table == "market_cap":

        df.columns = [
            "id",
            "company_id",
            "year",
            "market_cap",
            "enterprise_value",
            "pe_ratio",
            "pb_ratio",
            "dividend_yield",
            "other_ratio"
        ]


    return df



def insert_table(df, table):

    conn = sqlite3.connect(
        DATABASE
    )


    df.to_sql(
        table,
        conn,
        if_exists="append",
        index=False
    )


    conn.close()



def run_loader():

    files = os.listdir(
        RAW_PATH
    )


    audit = []


    for file in files:


        if file.endswith(".xlsx"):


            try:

                print(
                    f"Loading {file}"
                )


                df = load_excel(
                    file
                )


                df = clean_columns(
                    df
                )


                table = file.replace(
                    ".xlsx",
                    ""
                ).lower()


                df = fix_special_tables(
                    df,
                    table
                )


                insert_table(
                    df,
                    table
                )


                audit.append(
                    {
                        "file": file,
                        "rows": len(df),
                        "status": "loaded"
                    }
                )


            except Exception as e:


                print(
                    "\nFAILED:",
                    file
                )

                traceback.print_exc()


                audit.append(
                    {
                        "file": file,
                        "rows": 0,
                        "status": str(e)
                    }
                )


    os.makedirs(
        "output",
        exist_ok=True
    )


    pd.DataFrame(
        audit
    ).to_csv(
        "output/load_audit.csv",
        index=False
    )



if __name__ == "__main__":

    run_loader()

    print(
        "ETL Load Completed"
    )