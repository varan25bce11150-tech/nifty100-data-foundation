"""
Sprint 7 - Day 42
Portfolio Summary Report

Generates a full-universe summary for the authoritative 92-company
universe:
- header (company count, sector count, total market cap);
- average market metrics strip;
- average quality and market-cap bar charts by sector;
- top-10 companies by quality table;
- output/portfolio_summary.csv with one row per company (latest
  figures, optionally enriched with Sprint 6 cluster labels).

Validation: the universe must contain exactly 92 unique companies, the
CSV must contain exactly 92 rows, and every output file must exist.

Output:
    reports/portfolio_summary.png
    output/portfolio_summary.csv
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.reports import charts
from src.reports.data import (
    DB_PATH,
    OUTPUT_DIR,
    RATIO_FIELDS,
    load_cluster_labels,
    load_companies,
    load_latest_snapshot,
    validate_universe,
)
from src.reports.styles import (
    GREY,
    HEADER_BG,
    NAVY,
    format_cr,
    format_percent,
    format_ratio,
    save_figure,
)

REPORTS_DIR = "reports"
PORTFOLIO_FILE = os.path.join(REPORTS_DIR, "portfolio_summary.png")
PORTFOLIO_CSV = os.path.join(OUTPUT_DIR, "portfolio_summary.csv")

TOP_TABLE_LIMIT = 10


# ==========================================================
# DATA PREPARATION
# ==========================================================

def _sector_averages(snapshot: pd.DataFrame) -> pd.DataFrame:
    """Average quality score per sector (sorted descending)."""
    grouped = (
        snapshot.groupby("broad_sector")
        .agg(
            company_count=("company_id", "count"),
            avg_quality=("composite_quality_score", "mean"),
            avg_roe=("return_on_equity_pct", "mean"),
            total_market_cap=("market_cap", "sum"),
        )
        .reset_index()
    )

    return grouped.sort_values("avg_quality", ascending=False)


def _top_companies(snapshot: pd.DataFrame) -> pd.DataFrame:
    """Return the top companies in the universe by quality score."""
    table = snapshot.sort_values(
        "composite_quality_score", ascending=False
    ).head(TOP_TABLE_LIMIT)

    return table[
        [
            "company_name",
            "broad_sector",
            "industry",
            "return_on_equity_pct",
            "return_on_capital_employed_pct",
            "composite_quality_score",
            "market_cap",
        ]
    ]


def build_summary_dataframe(db_path: str = DB_PATH) -> pd.DataFrame:
    """Build the one-row-per-company summary CSV frame.

    The authoritative universe (92 companies) is enriched with the latest
    ratio and market-cap figures, plus Sprint 6 cluster labels when the
    generated cluster_labels.csv is available.
    """
    snapshot = load_latest_snapshot(db_path)
    validate_universe(snapshot)

    cluster_labels = load_cluster_labels()

    if not cluster_labels.empty:
        snapshot = snapshot.merge(
            cluster_labels[["company_id", "cluster_id", "cluster_name"]],
            on="company_id",
            how="left",
        )
    else:
        snapshot["cluster_id"] = np.nan
        snapshot["cluster_name"] = None

    columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "industry",
        "ratio_year",
        *RATIO_FIELDS,
        "market_cap_year",
        "market_cap",
        "pe_ratio",
        "pb_ratio",
        "dividend_yield",
        "cluster_id",
        "cluster_name",
    ]

    return snapshot[columns]


# ==========================================================
# FIGURE DRAWING
# ==========================================================

def _draw_header(
    ax: plt.Axes,
    company_count: int,
    sector_count: int,
    total_market_cap: float,
) -> None:
    """Draw the navy header band for the portfolio summary."""
    ax.axis("off")
    ax.set_facecolor(HEADER_BG)

    ax.text(
        0.02,
        0.62,
        "Nifty100 Portfolio Summary",
        transform=ax.transAxes,
        fontsize=20,
        fontweight="bold",
        color="white",
        va="center",
    )

    ax.text(
        0.02,
        0.18,
        f"Companies: {company_count}    |    Sectors: {sector_count}"
        f"    |    Total Market Cap: {format_cr(total_market_cap)}",
        transform=ax.transAxes,
        fontsize=11,
        color="#D6E4F0",
        va="center",
    )


def _draw_metrics_strip(ax: plt.Axes, snapshot: pd.DataFrame) -> None:
    """Draw the average universe metrics as labelled KPI boxes."""
    ax.axis("off")

    metrics = [
        ("Avg ROE", format_percent(snapshot["return_on_equity_pct"].mean())),
        ("Avg ROCE", format_percent(snapshot["return_on_capital_employed_pct"].mean())),
        ("Avg OPM", format_percent(snapshot["operating_profit_margin_pct"].mean())),
        ("Avg NPM", format_percent(snapshot["net_profit_margin_pct"].mean())),
        ("Avg D/E", format_ratio(snapshot["debt_to_equity"].mean())),
        ("Avg Quality", format_ratio(snapshot["composite_quality_score"].mean())),
    ]

    count = len(metrics)
    width = 1.0 / count

    for index, (label, value) in enumerate(metrics):
        x = index * width

        ax.text(
            x + width / 2,
            0.66,
            label,
            transform=ax.transAxes,
            ha="center",
            fontsize=9,
            color=GREY,
        )
        ax.text(
            x + width / 2,
            0.30,
            value,
            transform=ax.transAxes,
            ha="center",
            fontsize=13,
            fontweight="bold",
            color=NAVY,
        )

    for index in range(1, count):
        ax.axvline(
            index * width,
            ymin=0.05,
            ymax=0.95,
            color="#DDDDDD",
            linewidth=1,
        )


def _draw_top_companies_table(
    ax: plt.Axes,
    table: pd.DataFrame,
) -> None:
    """Draw the top companies table."""
    ax.axis("off")

    if table.empty:
        ax.text(
            0.5,
            0.5,
            "No quality data available",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=11,
            color=GREY,
        )
        return

    columns = [
        ("Company", "company_name"),
        ("Sector", "broad_sector"),
        ("Industry", "industry"),
        ("ROE", "return_on_equity_pct"),
        ("ROCE", "return_on_capital_employed_pct"),
        ("Quality", "composite_quality_score"),
        ("Mkt Cap", "market_cap"),
    ]

    header = [label for label, _ in columns]

    cell_text = []
    for _, row in table.iterrows():
        cells = []
        for label, column in columns:
            value = row.get(column)
            if label == "Mkt Cap":
                cells.append(format_cr(value))
            elif label in ("Company", "Sector", "Industry"):
                cells.append(str(value) if value == value else "N/A")
            else:
                cells.append(
                    "N/A" if value is None or value != value else f"{float(value):.1f}"
                )
        cell_text.append(cells)

    tbl = ax.table(
        cellText=cell_text,
        colLabels=header,
        loc="center",
        cellLoc="left",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.4)

    for (row_idx, col_idx), cell in tbl.get_celld().items():
        if row_idx == 0:
            cell.set_facecolor(NAVY)
            cell.set_text_props(color="white", fontweight="bold")
        elif row_idx % 2 == 0:
            cell.set_facecolor("#F2F5F8")


def _draw_footer(ax: plt.Axes) -> None:
    """Draw the generation footer."""
    ax.axis("off")
    ax.text(
        0.02,
        0.5,
        "Generated by Nifty100 Financial Analytics Platform  |  Sprint 7 - "
        "Automated Report Generation",
        transform=ax.transAxes,
        fontsize=8,
        color=GREY,
        va="center",
    )


# ==========================================================
# REPORT GENERATION
# ==========================================================

def generate_portfolio_summary(
    db_path: str = DB_PATH,
    report_dir: Optional[str] = None,
    csv_dir: Optional[str] = None,
) -> Tuple[str, str]:
    """Generate the portfolio summary PNG and CSV.

    Returns (png_path, csv_path).
    """
    if report_dir is None:
        report_dir = REPORTS_DIR

    if csv_dir is None:
        csv_dir = OUTPUT_DIR

    snapshot = load_latest_snapshot(db_path)
    validate_universe(snapshot)

    sector_summary = _sector_averages(snapshot)
    top_table = _top_companies(snapshot)

    total_market_cap = float(snapshot["market_cap"].sum(skipna=True))
    sector_count = int(snapshot["broad_sector"].nunique())

    os.makedirs(report_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)

    fig = plt.figure(figsize=(12, 13))
    grid = fig.add_gridspec(
        6,
        1,
        height_ratios=[1.0, 1.0, 3.0, 3.0, 2.6, 0.4],
        hspace=0.55,
    )

    header_ax = fig.add_subplot(grid[0, 0])
    metrics_ax = fig.add_subplot(grid[1, 0])
    quality_ax = fig.add_subplot(grid[2, 0])
    market_ax = fig.add_subplot(grid[3, 0])
    table_ax = fig.add_subplot(grid[4, 0])
    footer_ax = fig.add_subplot(grid[5, 0])

    _draw_header(
        header_ax,
        len(snapshot),
        sector_count,
        total_market_cap,
    )
    _draw_metrics_strip(metrics_ax, snapshot)

    quality_ax.text(
        0.02,
        0.96,
        "Average Quality Score by Sector",
        transform=quality_ax.transAxes,
        fontsize=11,
        fontweight="bold",
        color=NAVY,
        va="top",
    )
    charts.quality_bar(
        sector_summary,
        label_column="broad_sector",
        value_column="avg_quality",
        title="",
        xlabel="Average Quality Score",
        ax=quality_ax,
    )

    market_ax.text(
        0.02,
        0.96,
        "Total Market Cap by Sector",
        transform=market_ax.transAxes,
        fontsize=11,
        fontweight="bold",
        color=NAVY,
        va="top",
    )
    charts.quality_bar(
        sector_summary,
        label_column="broad_sector",
        value_column="total_market_cap",
        title="",
        xlabel="Market Cap",
        ax=market_ax,
    )

    _draw_top_companies_table(table_ax, top_table)
    _draw_footer(footer_ax)

    png_path = os.path.join(report_dir, "portfolio_summary.png")
    save_figure(fig, png_path)

    summary = build_summary_dataframe(db_path)
    csv_path = os.path.join(csv_dir, "portfolio_summary.csv")
    summary.to_csv(csv_path, index=False)

    return png_path, csv_path


# ==========================================================
# VALIDATION
# ==========================================================

def validate_outputs(
    png_path: str,
    csv_path: str,
    expected_companies: int = 92,
) -> Dict[str, bool]:
    """Validate the generated portfolio summary outputs.

    Returns a dictionary of check name -> passed flag. Raises nothing:
    callers decide what to do with failed checks.
    """
    checks: Dict[str, bool] = {}

    checks["PNG exists"] = os.path.exists(png_path)
    checks["CSV exists"] = os.path.exists(csv_path)

    if not os.path.exists(csv_path):
        checks["CSV rows = 92"] = False
        checks["Unique companies = 92"] = False
        checks["No missing cluster data"] = False
        return checks

    summary = pd.read_csv(csv_path)

    checks["CSV rows = 92"] = len(summary) == expected_companies
    checks["Unique companies = 92"] = (
        summary["company_id"].nunique() == expected_companies
    )
    checks["No missing cluster data"] = (
        "cluster_name" in summary.columns
        and int(summary["cluster_name"].isna().sum()) == 0
    )

    return checks


# ==========================================================
# ENTRY POINT
# ==========================================================

def main() -> None:
    print("Generating portfolio summary...")

    png_path, csv_path = generate_portfolio_summary()

    checks = validate_outputs(png_path, csv_path)

    print("")
    print("PORTFOLIO SUMMARY STATUS")
    print("------------------------")
    for check, passed in checks.items():
        print(f"{check}: {'PASS' if passed else 'FAIL'}")

    print(f"\nCreated: {png_path}")
    print(f"Created: {csv_path}")

    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(
            f"Portfolio summary validation failed at: {', '.join(failed)}"
        )


if __name__ == "__main__":
    main()
