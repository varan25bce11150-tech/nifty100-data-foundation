"""
Sprint 7 - Day 42
Sector Report

Generates a one-page PNG report per sector containing:
- sector header (name, company count, total market cap);
- average financial metrics strip (ROE, ROCE, margins, D/E, quality);
- a quality ranking bar chart of every company in the sector;
- the top companies table by quality score.

Output:
    reports/sectors/<sector_slug>_report.png
"""

from __future__ import annotations

import os
import re
from typing import Dict, List, Optional

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from src.reports import charts
from src.reports.data import (
    DB_PATH,
    load_latest_snapshot,
    load_sector_names,
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
SECTOR_DIR = os.path.join(REPORTS_DIR, "sectors")

TABLE_ROW_LIMIT = 10


# ==========================================================
# HELPERS
# ==========================================================

def _slug(name: str) -> str:
    """Convert a sector name into a filesystem-safe slug."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _format_table_value(value, decimals: int = 1) -> str:
    if value is None or value != value:
        return "N/A"
    return f"{float(value):.{decimals}f}"


def _build_sector_data(
    sector: str,
    db_path: str = DB_PATH,
) -> Dict[str, object]:
    """Assemble the data needed for one sector report.

    Raises ValueError when the sector is unknown.
    """
    snapshot = load_latest_snapshot(db_path)

    sector_data = snapshot[snapshot["broad_sector"] == sector].copy()

    if sector_data.empty:
        raise ValueError(
            f"Unknown sector '{sector}'. It is not present in the sectors table."
        )

    return {
        "sector": sector,
        "companies": sector_data,
        "company_count": len(sector_data),
        "total_market_cap": float(
            sector_data["market_cap"].sum(skipna=True)
        ),
        "averages": {
            "return_on_equity_pct": sector_data["return_on_equity_pct"].mean(),
            "return_on_capital_employed_pct": sector_data[
                "return_on_capital_employed_pct"
            ].mean(),
            "operating_profit_margin_pct": sector_data[
                "operating_profit_margin_pct"
            ].mean(),
            "net_profit_margin_pct": sector_data["net_profit_margin_pct"].mean(),
            "debt_to_equity": sector_data["debt_to_equity"].mean(),
            "composite_quality_score": sector_data["composite_quality_score"].mean(),
        },
    }


def _top_companies_table(data: Dict[str, object]) -> pd.DataFrame:
    """Return the top companies in the sector by quality score."""
    companies = data["companies"]

    columns = [
        "company_name",
        "industry",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "operating_profit_margin_pct",
        "composite_quality_score",
        "market_cap",
    ]

    table = companies[columns].copy()
    table = table.sort_values(
        "composite_quality_score", ascending=False
    )
    table = table.head(TABLE_ROW_LIMIT)

    return table


# ==========================================================
# FIGURE DRAWING
# ==========================================================

def _draw_header(
    ax: plt.Axes,
    sector: str,
    company_count: int,
    total_market_cap: float,
) -> None:
    """Draw the navy header band for the sector."""
    ax.axis("off")
    ax.set_facecolor(HEADER_BG)

    ax.text(
        0.02,
        0.62,
        f"{sector} Sector Report",
        transform=ax.transAxes,
        fontsize=20,
        fontweight="bold",
        color="white",
        va="center",
    )

    ax.text(
        0.02,
        0.18,
        f"Companies: {company_count}    |    "
        f"Total Market Cap: {format_cr(total_market_cap)}",
        transform=ax.transAxes,
        fontsize=11,
        color="#D6E4F0",
        va="center",
    )


def _draw_metrics_strip(ax: plt.Axes, averages: Dict[str, float]) -> None:
    """Draw the average sector metrics as labelled KPI boxes."""
    ax.axis("off")

    metrics = [
        ("Avg ROE", format_percent(averages["return_on_equity_pct"])),
        ("Avg ROCE", format_percent(averages["return_on_capital_employed_pct"])),
        ("Avg OPM", format_percent(averages["operating_profit_margin_pct"])),
        ("Avg NPM", format_percent(averages["net_profit_margin_pct"])),
        ("Avg D/E", format_ratio(averages["debt_to_equity"])),
        ("Avg Quality", format_ratio(averages["composite_quality_score"])),
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


def _draw_companies_table(
    ax: plt.Axes,
    table: pd.DataFrame,
) -> None:
    """Draw the top companies table."""
    ax.axis("off")

    if table.empty:
        ax.text(
            0.5,
            0.5,
            "No companies with quality data",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=11,
            color=GREY,
        )
        return

    columns = [
        ("Company", "company_name"),
        ("Industry", "industry"),
        ("ROE", "return_on_equity_pct"),
        ("ROCE", "return_on_capital_employed_pct"),
        ("OPM", "operating_profit_margin_pct"),
        ("Quality", "composite_quality_score"),
        ("Mkt Cap", "market_cap"),
    ]

    header = [label for label, _ in columns]

    cell_text = []
    for _, row in table.iterrows():
        cells = []
        for label, column in columns:
            value = row.get(column)
            if label in ("Mkt Cap",):
                cells.append(format_cr(value))
            elif label in ("Company", "Industry"):
                cells.append(str(value) if value == value else "N/A")
            else:
                cells.append(_format_table_value(value))
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
# SECTOR REPORT GENERATION
# ==========================================================

def generate_sector_report(
    sector: str,
    db_path: str = DB_PATH,
    output_dir: Optional[str] = None,
) -> str:
    """Generate the one-page PNG report for a single sector.

    Returns the path of the generated file.
    """
    if output_dir is None:
        output_dir = SECTOR_DIR

    data = _build_sector_data(sector, db_path)

    os.makedirs(output_dir, exist_ok=True)

    fig = plt.figure(figsize=(12, 12))
    grid = fig.add_gridspec(
        5,
        1,
        height_ratios=[1.0, 1.0, 3.4, 2.8, 0.4],
        hspace=0.55,
    )

    header_ax = fig.add_subplot(grid[0, 0])
    metrics_ax = fig.add_subplot(grid[1, 0])
    chart_ax = fig.add_subplot(grid[2, 0])
    table_ax = fig.add_subplot(grid[3, 0])
    footer_ax = fig.add_subplot(grid[4, 0])

    _draw_header(
        header_ax,
        data["sector"],
        data["company_count"],
        data["total_market_cap"],
    )
    _draw_metrics_strip(metrics_ax, data["averages"])

    chart_ax.text(
        0.02,
        0.96,
        "Company Quality Ranking",
        transform=chart_ax.transAxes,
        fontsize=11,
        fontweight="bold",
        color=NAVY,
        va="top",
    )

    chart_fig = charts.quality_bar(
        data["companies"],
        label_column="company_name",
        value_column="composite_quality_score",
        title="",
        xlabel="Quality Score",
        ax=chart_ax,
    )

    if chart_fig is None:
        chart_ax.text(
            0.5,
            0.4,
            "No quality data available",
            transform=chart_ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
            color=GREY,
        )

    _draw_companies_table(table_ax, _top_companies_table(data))
    _draw_footer(footer_ax)

    output_path = os.path.join(output_dir, f"{_slug(sector)}_report.png")
    save_figure(fig, output_path)

    return output_path


# ==========================================================
# BATCH GENERATION
# ==========================================================

def generate_all_sector_reports(
    db_path: str = DB_PATH,
    output_dir: Optional[str] = None,
) -> List[str]:
    """Generate a report for every sector in the sectors table.

    Returns the list of generated file paths.
    """
    if output_dir is None:
        output_dir = SECTOR_DIR

    sector_names = load_sector_names(db_path)

    paths: List[str] = []

    for index, sector in enumerate(sector_names, start=1):
        path = generate_sector_report(sector, db_path, output_dir)
        paths.append(path)
        print(f"[{index}/{len(sector_names)}] {sector} -> {path}")

    return paths


# ==========================================================
# ENTRY POINT
# ==========================================================

def main() -> None:
    print("Generating sector reports...")

    sector_names = load_sector_names()
    print(f"Sectors: {len(sector_names)}")

    paths = generate_all_sector_reports()

    print(f"Generated: {len(paths)} sector reports")
    print(f"Directory: {SECTOR_DIR}")


if __name__ == "__main__":
    main()
