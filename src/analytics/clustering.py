"""
Sprint 6 - Day 36
KMeans Financial Clustering

Features:
- Return on Equity
- Debt to Equity
- Revenue CAGR (5Y)
- FCF CAGR (5Y)
- Operating Profit Margin

Pipeline:
1.  Load the authoritative 92-company universe from `companies`.
2.  Load the latest financial ratios per company.
3.  Calculate Revenue CAGR (5Y) from `profitandloss`.
4.  Calculate FCF CAGR (5Y) from `cashflow`.
5.  Impute missing values using sector medians (global median fallback).
6.  Winsorize extreme feature values (5th/95th percentiles).
7.  Standardize features with StandardScaler.
8.  Run KMeans with k=5, random_state=42, n_init=10.
9.  Calculate each company's distance from its cluster centroid.
10. Generate cluster profiles.
11. Assign data-driven cluster names.
12. Generate elbow_plot.png, cluster_labels.csv and cluster_profiles.csv.
13. Validate every output and print the Sprint 6 status report.
"""

from __future__ import annotations

import os
import re
import sqlite3
from typing import Dict, List, Optional

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# ==========================================================
# CONFIGURATION
# ==========================================================

DB_PATH = "nifty100.db"

EXPECTED_COMPANY_COUNT = 92
CLUSTER_COUNT = 5
RANDOM_STATE = 42
N_INIT = 10

ELBOW_MIN_CLUSTERS = 2
ELBOW_MAX_CLUSTERS = 10

OUTPUT_DIR = "output"
REPORTS_DIR = "reports"

CLUSTER_LABEL_FILE = os.path.join(OUTPUT_DIR, "cluster_labels.csv")
CLUSTER_PROFILE_FILE = os.path.join(OUTPUT_DIR, "cluster_profiles.csv")
ELBOW_FILE = os.path.join(REPORTS_DIR, "elbow_plot.png")

# Robust winsorization bounds. The 5th/95th percentiles are used instead of
# the 1st/99th because the 92-company universe is small: with n=92 the 99th
# percentile is effectively the maximum value, so 1st/99th clipping would
# barely tame the extreme outliers (historical ROE spikes such as BEL ~4379%,
# HAL ~3669% and INDIGO ~857%).
WINSOR_LOWER_QUANTILE = 0.05
WINSOR_UPPER_QUANTILE = 0.95

# Cluster-name classification thresholds based on the financial meaning of
# each feature (see assign_cluster_names).
LEVERAGED_DEBT_THRESHOLD = 1.5
LEVERAGED_GROWTH_THRESHOLD = 5.0
HIGH_MARGIN_THRESHOLD = 55.0
HIGH_ROE_THRESHOLD = 35.0
FCF_GROWTH_THRESHOLD = 20.0
LOW_GROWTH_THRESHOLD = 8.0


# ==========================================================
# FEATURES
# ==========================================================

FEATURE_COLUMNS = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


# ==========================================================
# YEAR EXTRACTION
# ==========================================================

def extract_year(value: object) -> Optional[int]:
    """Safely extract a year from a stored date string.

    Examples:
        "Mar 2024" -> 2024
        "Dec 2023" -> 2023
        "Mar-13"   -> 2013
        "TTM"      -> None
        None/NaN   -> None

    The helper never raises: integers, floats, None, NaN and unexpected
    strings simply yield None when no year can be extracted.
    """
    if value is None:
        return None

    text = str(value).strip()

    if not text or text.lower() in ("nan", "nat", "none"):
        return None

    # Prefer the last four-digit year, e.g. "Mar 2024" -> 2024.
    years = re.findall(r"\b(?:19|20)\d{2}\b", text)
    if years:
        return int(years[-1])

    # Two-digit suffix, e.g. "Mar-13" -> 2013.
    match = re.search(r"[-/]\s*(\d{2})$", text)
    if match:
        year = int(match.group(1))
        return 2000 + year if year <= 30 else 1900 + year

    return None


# ==========================================================
# REVENUE CAGR
# ==========================================================

def calculate_revenue_cagr(profitandloss: pd.DataFrame) -> pd.DataFrame:
    """Calculate the latest available 5-year Revenue CAGR per company.

    CAGR = ((end_sales / start_sales) ** (1 / 5) - 1) * 100

    Rules:
    - Calendar years are extracted from the stored `year` text, so both
      text ("Mar 2024") and integer (2024) years are handled safely.
    - TTM and unparseable years are ignored for historical CAGR.
    - The beginning year must be exactly 5 years before the ending year.
    - Beginning sales must be positive.
    - The latest valid 5-year window is kept per company.
    - Infinite / NaN results are never emitted.
    """
    df = profitandloss.copy()
    df["calendar_year"] = df["year"].apply(extract_year)
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    df = df.dropna(subset=["company_id", "calendar_year", "sales"])

    rows: List[Dict[str, object]] = []

    for company_id, group in df.groupby("company_id"):
        yearly = group.groupby("calendar_year")["sales"].mean().sort_index()

        for end_year in yearly.index:
            start_year = end_year - 5

            if start_year not in yearly.index:
                continue

            start_sales = float(yearly.loc[start_year])
            end_sales = float(yearly.loc[end_year])

            if start_sales <= 0 or end_sales < 0:
                continue

            try:
                cagr = (end_sales / start_sales) ** (1 / 5) - 1
                cagr = cagr * 100
            except (ValueError, ZeroDivisionError, OverflowError):
                continue

            if np.isfinite(cagr):
                rows.append({
                    "company_id": company_id,
                    "end_year": int(end_year),
                    "revenue_cagr_5yr": round(float(cagr), 2),
                })

    result = pd.DataFrame(rows)

    if result.empty:
        return pd.DataFrame(columns=["company_id", "revenue_cagr_5yr"])

    result = result.sort_values(["company_id", "end_year"])
    result = result.drop_duplicates(subset=["company_id"], keep="last")

    return result[["company_id", "revenue_cagr_5yr"]]


# ==========================================================
# FCF CAGR
# ==========================================================

def calculate_fcf_cagr(cashflow: pd.DataFrame) -> pd.DataFrame:
    """Calculate the latest available 5-year FCF CAGR per company.

    FCF = operating_activity + investing_activity

    CAGR is only mathematically meaningful when the beginning FCF is
    positive. If the beginning FCF is <= 0, or the ending FCF is negative,
    the company is excluded rather than producing a misleading or infinite
    value.
    """
    df = cashflow.copy()
    df["calendar_year"] = df["year"].apply(extract_year)
    df["operating_activity"] = pd.to_numeric(df["operating_activity"], errors="coerce")
    df["investing_activity"] = pd.to_numeric(df["investing_activity"], errors="coerce")
    df["fcf"] = df["operating_activity"] + df["investing_activity"]
    df = df.dropna(subset=["company_id", "calendar_year", "fcf"])

    rows: List[Dict[str, object]] = []

    for company_id, group in df.groupby("company_id"):
        yearly = group.groupby("calendar_year")["fcf"].mean().sort_index()

        for end_year in yearly.index:
            start_year = end_year - 5

            if start_year not in yearly.index:
                continue

            start_fcf = float(yearly.loc[start_year])
            end_fcf = float(yearly.loc[end_year])

            if start_fcf <= 0 or end_fcf < 0:
                continue

            try:
                cagr = (end_fcf / start_fcf) ** (1 / 5) - 1
                cagr = cagr * 100
            except (ValueError, ZeroDivisionError, OverflowError):
                continue

            if np.isfinite(cagr):
                rows.append({
                    "company_id": company_id,
                    "end_year": int(end_year),
                    "fcf_cagr_5yr": round(float(cagr), 2),
                })

    result = pd.DataFrame(rows)

    if result.empty:
        return pd.DataFrame(columns=["company_id", "fcf_cagr_5yr"])

    result = result.sort_values(["company_id", "end_year"])
    result = result.drop_duplicates(subset=["company_id"], keep="last")

    return result[["company_id", "fcf_cagr_5yr"]]


# ==========================================================
# LOAD DATA
# ==========================================================

def load_data(db_path: str = DB_PATH) -> pd.DataFrame:
    """Load the complete 92-company clustering dataset from SQLite.

    The authoritative universe comes from `companies` (joined with `sectors`
    for sector information), not from `financial_ratios` or `cashflow`.
    """
    conn = sqlite3.connect(db_path)

    try:
        companies = pd.read_sql_query(
            """
            SELECT
                c.id AS company_id,
                c.company_name,
                s.sector AS broad_sector,
                s.industry AS sub_sector
            FROM companies c
            LEFT JOIN sectors s
                ON c.id = s.company_id
            """,
            conn,
        )

        ratios = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                return_on_equity_pct,
                debt_to_equity,
                operating_profit_margin_pct
            FROM financial_ratios
            """,
            conn,
        )

        cashflow = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                operating_activity,
                investing_activity
            FROM cashflow
            """,
            conn,
        )

        profitandloss = pd.read_sql_query(
            """
            SELECT
                company_id,
                year,
                sales
            FROM profitandloss
            """,
            conn,
        )
    finally:
        conn.close()

    valid_company_ids = set(companies["company_id"])

    # Restrict every source table to the authoritative company universe.
    ratios = ratios[ratios["company_id"].isin(valid_company_ids)].copy()
    cashflow = cashflow[cashflow["company_id"].isin(valid_company_ids)].copy()
    profitandloss = profitandloss[profitandloss["company_id"].isin(valid_company_ids)].copy()

    # Latest ratio record per company. Years are extracted first so text
    # years ("Mar 2024") and integer years are both sorted safely; rows
    # without an extractable year (e.g. TTM) sort last and represent the
    # most recent period when present.
    ratios["calendar_year"] = ratios["year"].apply(extract_year)
    ratios = ratios.sort_values(
        ["company_id", "calendar_year"],
        na_position="last",
    )
    latest_ratios = ratios.drop_duplicates(subset=["company_id"], keep="last")

    revenue_cagr = calculate_revenue_cagr(profitandloss)
    fcf_cagr = calculate_fcf_cagr(cashflow)

    data = companies.merge(latest_ratios, on="company_id", how="left")
    data = data.merge(revenue_cagr, on="company_id", how="left")
    data = data.merge(fcf_cagr, on="company_id", how="left")

    return data


# ==========================================================
# SECTOR MEDIAN IMPUTATION
# ==========================================================

def impute_sector_medians(data: pd.DataFrame) -> pd.DataFrame:
    """Fill missing feature values with sector medians.

    For every feature, missing values are replaced by the median of the
    company's broad sector. If the sector median is itself unavailable
    (the whole sector is missing), the global median is used instead.
    """
    result = data.copy()

    for feature in FEATURE_COLUMNS:
        result[feature] = pd.to_numeric(result[feature], errors="coerce")

        sector_median = (
            result.groupby("broad_sector")[feature].transform("median")
        )
        result[feature] = result[feature].fillna(sector_median)
        result[feature] = result[feature].fillna(result[feature].median())

    return result


# ==========================================================
# ROBUST WINSORIZATION
# ==========================================================

def winsorize_features(
    data: pd.DataFrame,
    lower_quantile: float = WINSOR_LOWER_QUANTILE,
    upper_quantile: float = WINSOR_UPPER_QUANTILE,
) -> pd.DataFrame:
    """Clip extreme feature values to robust percentile bounds.

    The clustering features contain extreme outliers (e.g. historical ROE
    spikes above 1000%). Without clipping, a handful of companies would
    dominate the distance calculations in KMeans. Values below/above the
    5th/95th percentiles are clamped to those bounds.

    The operation is deterministic: the same input always yields the same
    output, and no companies are deleted.
    """
    result = data.copy()

    for feature in FEATURE_COLUMNS:
        lower = result[feature].quantile(lower_quantile)
        upper = result[feature].quantile(upper_quantile)
        result[feature] = result[feature].clip(lower=lower, upper=upper)

    return result


# ==========================================================
# ELBOW PLOT
# ==========================================================

def run_elbow_analysis(features: np.ndarray) -> None:
    """Generate the KMeans elbow plot for k=2..10."""
    inertias: List[float] = []
    ks = list(range(ELBOW_MIN_CLUSTERS, ELBOW_MAX_CLUSTERS + 1))

    for k in ks:
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=N_INIT)
        model.fit(features)
        inertias.append(float(model.inertia_))

    os.makedirs(REPORTS_DIR, exist_ok=True)

    plt.figure(figsize=(9, 6))
    plt.plot(ks, inertias, marker="o")
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia")
    plt.title("KMeans Elbow Plot")
    plt.xticks(ks)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(ELBOW_FILE, dpi=150)
    plt.close()


# ==========================================================
# CLUSTER PROFILES
# ==========================================================

def create_cluster_profiles(data: pd.DataFrame) -> pd.DataFrame:
    """Create readable financial profiles for each cluster."""
    profiles = data.groupby("cluster_id")[FEATURE_COLUMNS].mean().round(2)
    profiles.insert(1, "company_count", data.groupby("cluster_id").size())
    return profiles.reset_index()


# ==========================================================
# DATA-DRIVEN CLUSTER NAMES
# ==========================================================

_DOMINANT_FEATURE_LABELS = {
    "return_on_equity_pct": "High ROE",
    "debt_to_equity": "High Debt",
    "revenue_cagr_5yr": "High Growth",
    "fcf_cagr_5yr": "FCF Growth",
    "operating_profit_margin_pct": "High Margin",
}


def _classify_cluster(row: pd.Series, profiles: pd.DataFrame, used: set[str]) -> str:
    """Classify one cluster profile into a descriptive name.

    Rules are evaluated in priority order and every name is used at most
    once, so clusters always receive distinct, descriptive labels.
    """
    rules = [
        (
            "Leveraged Growth",
            row["debt_to_equity"] >= LEVERAGED_DEBT_THRESHOLD
            and row["revenue_cagr_5yr"] >= LEVERAGED_GROWTH_THRESHOLD,
        ),
        (
            "High-Margin Businesses",
            row["operating_profit_margin_pct"] >= HIGH_MARGIN_THRESHOLD,
        ),
        (
            "High ROE Compounders",
            row["return_on_equity_pct"] >= HIGH_ROE_THRESHOLD,
        ),
        (
            "FCF Growth Leaders",
            row["fcf_cagr_5yr"] >= FCF_GROWTH_THRESHOLD,
        ),
        (
            "Low Growth / Core",
            row["revenue_cagr_5yr"] < LOW_GROWTH_THRESHOLD
            or row["fcf_cagr_5yr"] < 0.0,
        ),
        ("Balanced / Core", True),
    ]

    for name, condition in rules:
        if condition and name not in used:
            return name

    # Safety net (only reachable with more than six clusters): describe the
    # cluster by its single most distinctive feature.
    dominant = max(
        FEATURE_COLUMNS,
        key=lambda feature: abs(row[feature] - profiles[feature].median()),
    )
    return f"{_DOMINANT_FEATURE_LABELS[dominant]} Focus"


def assign_cluster_names(data: pd.DataFrame) -> Dict[int, str]:
    """Assign descriptive names using actual cluster characteristics.

    Names are derived from the average financial profile of each cluster,
    not from the arbitrary KMeans cluster id. Cluster names are analytical
    descriptions only; they are not investment recommendations.
    """
    profiles = data.groupby("cluster_id")[FEATURE_COLUMNS].mean()

    names: Dict[int, str] = {}
    used: set[str] = set()

    for cluster_id in sorted(profiles.index):
        row = profiles.loc[cluster_id]
        name = _classify_cluster(row, profiles, used)
        names[int(cluster_id)] = name
        used.add(name)

    return names


# ==========================================================
# ENSURE UNIQUE CLUSTER NAMES
# ==========================================================

def make_unique_cluster_names(names: Dict[int, str]) -> Dict[int, str]:
    """Ensure every cluster has a unique descriptive name.

    This is a defensive safety net; assign_cluster_names already avoids
    duplicates in the normal case. If duplicates are somehow produced, a
    "Group N" suffix is appended (the "absolutely necessary" case).
    """
    result: Dict[int, str] = {}
    used: Dict[str, int] = {}

    for cluster_id in sorted(names):
        base_name = names[cluster_id]
        count = used.get(base_name, 0)

        if count == 0:
            result[cluster_id] = base_name
        else:
            result[cluster_id] = f"{base_name} Group {count + 1}"

        used[base_name] = count + 1

    return result


# ==========================================================
# VALIDATION
# ==========================================================

def validate_results(
    data: pd.DataFrame,
    output: pd.DataFrame,
    profiles: pd.DataFrame,
) -> Dict[str, bool]:
    """Validate the clustering outputs against the sprint requirements.

    Returns a dictionary of check name -> passed flag.
    """
    checks: Dict[str, bool] = {}

    checks["Companies = 92"] = len(data) == EXPECTED_COMPANY_COUNT
    checks["Unique companies = 92"] = (
        data["company_id"].nunique() == EXPECTED_COMPANY_COUNT
    )
    checks["Clusters = 5"] = output["cluster_id"].nunique() == CLUSTER_COUNT
    checks["Missing clustering values = 0"] = (
        int(data[FEATURE_COLUMNS].isna().sum().sum()) == 0
    )
    checks["Missing cluster names = 0"] = (
        int(output["cluster_name"].isna().sum()) == 0
    )

    distances = pd.to_numeric(output["distance_from_centroid"], errors="coerce")
    checks["Invalid distances = 0"] = (
        not bool(distances.isna().any())
        and bool(np.isfinite(distances.to_numpy(dtype=float)).all())
    )

    checks["cluster_labels rows = 92"] = len(output) == EXPECTED_COMPANY_COUNT
    checks["cluster_profiles rows = 5"] = len(profiles) == CLUSTER_COUNT
    checks["One cluster per company"] = bool(output["company_id"].is_unique)

    return checks


def print_status_report(stages: Dict[str, bool]) -> None:
    """Print the Sprint 6 status report."""
    print("\nSPRINT 6 STATUS")
    print("----------------")

    for stage, passed in stages.items():
        print(f"{stage}: {'PASS' if passed else 'FAIL'}")


# ==========================================================
# MAIN PIPELINE
# ==========================================================

def run(db_path: str = DB_PATH) -> pd.DataFrame:
    """Run the complete clustering pipeline."""
    stages: Dict[str, bool] = {}

    print("Loading clustering data...")
    data = load_data(db_path)

    company_count = len(data)
    print(f"Companies loaded: {company_count}")

    if company_count != EXPECTED_COMPANY_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_COMPANY_COUNT} companies in the authoritative "
            f"universe, but found {company_count}."
        )
    stages["Data loading"] = True

    stages["Revenue CAGR"] = bool(data["revenue_cagr_5yr"].notna().any())
    stages["FCF CAGR"] = bool(data["fcf_cagr_5yr"].notna().any())

    print("\nMissing values before imputation:")
    print(data[FEATURE_COLUMNS].isna().sum())

    data = impute_sector_medians(data)

    missing_after = int(data[FEATURE_COLUMNS].isna().sum().sum())
    stages["Sector imputation"] = missing_after == 0

    print("\nMissing values after imputation:")
    print(data[FEATURE_COLUMNS].isna().sum())

    if missing_after > 0:
        raise ValueError("Missing values remain after sector median imputation.")

    clustering_data = winsorize_features(data[["company_id"] + FEATURE_COLUMNS])

    winsor_finite = bool(
        np.isfinite(clustering_data[FEATURE_COLUMNS].to_numpy(dtype=float)).all()
    )
    stages["Winsorization"] = winsor_finite

    print("\nFeature ranges after robust winsorization:")
    print(clustering_data[FEATURE_COLUMNS].describe().round(2).to_string())

    scaler = StandardScaler()
    X = scaler.fit_transform(clustering_data[FEATURE_COLUMNS])
    stages["Standardization"] = True

    run_elbow_analysis(X)
    stages["Elbow analysis"] = os.path.exists(ELBOW_FILE)

    print("\nRunning KMeans...")

    model = KMeans(
        n_clusters=CLUSTER_COUNT,
        random_state=RANDOM_STATE,
        n_init=N_INIT,
    )
    cluster_ids = model.fit_predict(X)
    stages["KMeans"] = True

    distances = np.linalg.norm(X - model.cluster_centers_[cluster_ids], axis=1)
    stages["Centroid distance"] = bool(np.isfinite(distances).all())

    data["cluster_id"] = cluster_ids
    data["distance_from_centroid"] = np.round(distances, 4)

    # Profiles are computed on winsorized features so that extreme outliers
    # do not skew the cluster averages.
    profile_data = data.copy()

    for feature in FEATURE_COLUMNS:
        profile_data[feature] = clustering_data[feature]

    names = assign_cluster_names(profile_data)
    names = make_unique_cluster_names(names)

    name_count = len(names)
    unique_name_count = len(set(names.values()))
    stages["Cluster naming"] = (
        name_count == CLUSTER_COUNT and unique_name_count == CLUSTER_COUNT
    )

    data["cluster_name"] = data["cluster_id"].map(names)

    profiles = create_cluster_profiles(
        profile_data.assign(cluster_id=data["cluster_id"])
    )
    profiles["cluster_name"] = profiles["cluster_id"].map(names)
    profiles = profiles[
        [
            "cluster_id",
            "company_count",
            "return_on_equity_pct",
            "debt_to_equity",
            "revenue_cagr_5yr",
            "fcf_cagr_5yr",
            "operating_profit_margin_pct",
            "cluster_name",
        ]
    ]
    stages["Cluster profiles"] = len(profiles) == CLUSTER_COUNT

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    output = data[
        ["company_id", "cluster_id", "cluster_name", "distance_from_centroid"]
    ].copy()
    output.to_csv(CLUSTER_LABEL_FILE, index=False)
    profiles.to_csv(CLUSTER_PROFILE_FILE, index=False)

    stages["CSV generation"] = (
        os.path.exists(CLUSTER_LABEL_FILE)
        and os.path.exists(CLUSTER_PROFILE_FILE)
        and os.path.exists(ELBOW_FILE)
    )

    print("\nCluster counts:")
    print(output.groupby(["cluster_id", "cluster_name"]).size())

    print("\nCluster profiles:")
    print(profiles.to_string(index=False))

    checks = validate_results(data, output, profiles)
    stages["Validation"] = all(checks.values())

    print("\nValidation:")
    for check, passed in checks.items():
        print(f"  {check}: {'PASS' if passed else 'FAIL'}")

    print(f"\nCreated: {CLUSTER_LABEL_FILE}")
    print(f"Created: {CLUSTER_PROFILE_FILE}")
    print(f"Created: {ELBOW_FILE}")

    print_status_report(stages)

    if not all(stages.values()):
        failed = [name for name, passed in stages.items() if not passed]
        raise RuntimeError(f"Sprint 6 pipeline failed at: {', '.join(failed)}")

    return output


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    run()
