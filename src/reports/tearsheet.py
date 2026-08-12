"""
Sprint 7 - Day 42
Company Tearsheet Report

Generates a one-page PNG "tearsheet" per company containing:
- company header (name, sector, industry, market-cap category);
- key metrics strip (ROE, ROCE, margins, D/E, quality, market cap, PE);
- three trend charts (revenue & profit, returns, cash flow);
- the latest 8 years of financial history as a table;
- the generated pros & cons summary (Sprint 5).

Missing data is handled gracefully: companies without ratio or cash-flow
history (e.g. SBIN has no financial_ratios, ATGL has no cashflow) render
"N/A" / "No data available" instead of crashing.

Output:
    reports/tearsheets/<COMPANY_ID>_tearsheet.png
"""

from __future__ import annotations

import os
import textwrap
from typing import Dict, List, Optional, Union

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from src.reports import charts
from src.reports.data import (
    DB_PATH,
    load_cashflow_history,
    load_cluster_labels,
    load_companies,
    load_latest_snapshot,
    load_pnl_history,
    load_prosandcons,
    load_ratios_history,
    validate_universe,
)
from src.reports.styles import (
    GREEN,
    GREY,
    HEADER_BG,
    NAVY,
    RED,
    format_cr,
    format_percent,
    format_ratio,
    save_figure,
)

REPORTS_DIR = "reports"
TEARSHEET_DIR = os.path.join(REPORTS_DIR, "tearsheets")

TABLE_ROW_LIMIT = 8
TEXT_LIMIT = 600


# ==========================================================
# DATA PREPARATION
# ==========================================================

def _truncate(text: Optional[str], limit: int = TEXT_LIMIT) -> str:
    """Truncate long text (pros & cons) to a readable length."""
    if text is None:
        return "N/A"

    text = str(text).strip()

    if len(text) <= limit:
        return text

    return text[: limit - 3].rstrip() + "..."


def _build_tearsheet_data(
    company_id: str,
    db_path: str = DB_PATH,
) -> Dict[str, object]:
    """Assemble every piece of data needed for one tearsheet.

    Raises ValueError when the company id is not part of the
    authoritative universe.
    """
    snapshot = load_latest_snapshot(db_path)

    company = snapshot[snapshot["company_id"] == company_id]

    if company.empty:
        raise ValueError(
            f"Unknown company id '{company_id}'. It is not part of the "
            "authoritative 92-company universe."
        )

    row = company.iloc[0]

    ratios = load_ratios_history(db_path)
    pnl = load_pnl_history(db_path)
    cashflow = load_cashflow_history(db_path)
    proscons = load_prosandcons(db_path)
    cluster_labels = load_cluster_labels()

    company_ratios = ratios[ratios["company_id"] == company_id].copy()
    company_pnl = pnl[pnl["company_id"] == company_id].copy()
    company_cashflow = cashflow[cashflow["company_id"] == company_id].copy()
    company_proscons = proscons[proscons["company_id"] == company_id]

    cluster_name = None
    if not cluster_labels.empty:
        cluster_row = cluster_labels[cluster_labels["company_id"] == company_id]
        if not cluster_row.empty:
            cluster_name = cluster_row.iloc[0].get("cluster_name")

    pros = cons = None
    if not company_proscons.empty:
        pros = company_proscons.iloc[0].get("pros")
        cons = company_proscons.iloc[0].get("cons")

    return {
        "company_id": company_id,
        "company_name": str(row["company_name"]),
        "broad_sector": row.get("broad_sector"),
        "industry": row.get("industry"),
        "market_cap_category": row.get("market_cap_category"),
        "cluster_name": cluster_name,
        "ratios": company_ratios,
        "pnl": company_pnl,
        "cashflow": company_cashflow,
        "pros": pros,
        "cons": cons,
        "latest": {
            "return_on_equity_pct": row.get("return_on_equity_pct"),
            "return_on_capital_employed_pct": row.get(
                "return_on_capital_employed_pct"
            ),
            "operating_profit_margin_pct": row.get(
                "operating_profit_margin_pct"
            ),
            "net_profit_margin_pct": row.get("net_profit_margin_pct"),
            "debt_to_equity": row.get("debt_to_equity"),
            "composite_quality_score": row.get("composite_quality_score"),
            "market_cap": row.get("market_cap"),
            "pe_ratio": row.get("pe_ratio"),
        },
    }


def _history_table(
    data: Dict[str, object],
) -> pd.DataFrame:
    """Build the latest-N-years financial history table.

    Ratios and profit-and-loss data are merged on the extracted calendar
    year; the most recent TABLE_ROW_LIMIT rows are returned.
    """
    ratios = data["ratios"]
    pnl = data["pnl"]

    if ratios.empty and pnl.empty:
        return pd.DataFrame()

    frame = pd.DataFrame()

    if not ratios.empty:
        frame = ratios[
            [
                "company_id",
                "calendar_year",
                "return_on_equity_pct",
                "return_on_capital_employed_pct",
                "operating_profit_margin_pct",
                "net_profit_margin_pct",
                "debt_to_equity",
                "composite_quality_score",
            ]
        ].copy()

    if not pnl.empty:
        pnl_part = pnl[
            ["company_id", "calendar_year", "sales", "net_profit"]
        ].copy()

        if frame.empty:
            frame = pnl_part
        else:
            frame = frame.merge(
                pnl_part,
                on=["company_id", "calendar_year"],
                how="outer",
            )

    frame = frame.dropna(subset=["calendar_year"])
    frame = frame.sort_values("calendar_year", ascending=False)
    frame = frame.drop_duplicates(subset=["calendar_year"], keep="first")

    return frame.head(TABLE_ROW_LIMIT)


# ==========================================================
# FIGURE DRAWING
# ==========================================================

def _format_table_value(value, decimals: int = 1) -> str:
    if value is None or value != value:
        return "N/A"
    return f"{float(value):.{decimals}f}"


def _draw_header(ax: plt.Axes, data: Dict[str, object]) -> None:
    """Draw the navy header band with company identity."""
    ax.axis("off")
    ax.set_facecolor(HEADER_BG)

    ax.text(
        0.02,
        0.62,
        str(data["company_name"]),
        transform=ax.transAxes,
        fontsize=20,
        fontweight="bold",
        color="white",
        va="center",
    )

    subtitle_parts = []
    if data.get("broad_sector"):
        subtitle_parts.append(str(data["broad_sector"]))
    if data.get("industry"):
        subtitle_parts.append(str(data["industry"]))
    if data.get("market_cap_category"):
        subtitle_parts.append(str(data["market_cap_category"]))
    if data.get("cluster_name"):
        subtitle_parts.append(f"Cluster: {data['cluster_name']}")

    ax.text(
        0.02,
        0.18,
        "  |  ".join(subtitle_parts),
        transform=ax.transAxes,
        fontsize=11,
        color="#D6E4F0",
        va="center",
    )

    ax.text(
        0.98,
        0.62,
        str(data["company_id"]),
        transform=ax.transAxes,
        fontsize=16,
        fontweight="bold",
        color="white",
        ha="right",
        va="center",
    )


def _draw_metrics_strip(ax: plt.Axes, latest: Dict[str, float]) -> None:
    """Draw the key metrics strip as labelled KPI boxes."""
    ax.axis("off")

    metrics = [
        ("ROE", format_percent(latest.get("return_on_equity_pct"))),
        ("ROCE", format_percent(latest.get("return_on_capital_employed_pct"))),
        ("OPM", format_percent(latest.get("operating_profit_margin_pct"))),
        ("NPM", format_percent(latest.get("net_profit_margin_pct"))),
        ("D/E", format_ratio(latest.get("debt_to_equity"))),
        ("Quality", format_ratio(latest.get("composite_quality_score"))),
        ("Mkt Cap", format_cr(latest.get("market_cap"))),
        ("P/E", format_ratio(latest.get("pe_ratio"))),
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


def _draw_history_table(
    ax: plt.Axes,
    table: pd.DataFrame,
    year_column: str = "calendar_year",
) -> None:
    """Draw the financial history table."""
    ax.axis("off")

    if table is None or table.empty:
        ax.text(
            0.5,
            0.5,
            "No financial history available",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=11,
            color=GREY,
        )
        return

    columns = [
        ("Year", year_column),
        ("Sales", "sales"),
        ("Net Profit", "net_profit"),
        ("ROE", "return_on_equity_pct"),
        ("ROCE", "return_on_capital_employed_pct"),
        ("OPM", "operating_profit_margin_pct"),
        ("NPM", "net_profit_margin_pct"),
        ("D/E", "debt_to_equity"),
        ("Quality", "composite_quality_score"),
    ]

    header = [label for label, _ in columns]

    cell_text = []
    for _, row in table.iterrows():
        cell_text.append(
            [
                _format_table_value(row.get(column))
                for _, column in columns
            ]
        )

    tbl = ax.table(
        cellText=cell_text,
        colLabels=header,
        loc="center",
        cellLoc="center",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.35)

    for (row_idx, col_idx), cell in tbl.get_celld().items():
        if row_idx == 0:
            cell.set_facecolor(NAVY)
            cell.set_text_props(color="white", fontweight="bold")
        elif row_idx % 2 == 0:
            cell.set_facecolor("#F2F5F8")


def _draw_pros_cons(
    ax: plt.Axes,
    pros: Optional[str],
    cons: Optional[str],
) -> None:
    """Draw the pros & cons summary box with manually wrapped text."""
    ax.axis("off")

    ax.text(
        0.02,
        0.95,
        "PROS",
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        color=GREEN,
        va="top",
    )
    pros_text = textwrap.fill(_truncate(pros), width=95)
    ax.text(
        0.02,
        0.52,
        pros_text,
        transform=ax.transAxes,
        fontsize=8.5,
        va="top",
        color="#222222",
    )

    ax.text(
        0.52,
        0.95,
        "CONS",
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        color=RED,
        va="top",
    )
    cons_text = textwrap.fill(_truncate(cons), width=95)
    ax.text(
        0.52,
        0.52,
        cons_text,
        transform=ax.transAxes,
        fontsize=8.5,
        va="top",
        color="#222222",
    )


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
# TEARSHEET GENERATION
# ==========================================================

def generate_tearsheet(
    company_id: str,
    db_path: str = DB_PATH,
    output_dir: Optional[str] = None,
) -> str:
    """Generate the one-page tearsheet PNG for a single company.

    Returns the path of the generated file.
    """
    if output_dir is None:
        output_dir = TEARSHEET_DIR

    data = _build_tearsheet_data(company_id, db_path)

    os.makedirs(output_dir, exist_ok=True)

    fig = plt.figure(figsize=(12, 17))
    grid = fig.add_gridspec(
        8,
        1,
        height_ratios=[1.0, 1.0, 2.6, 2.6, 2.6, 2.2, 1.6, 0.4],
        hspace=0.55,
    )

    header_ax = fig.add_subplot(grid[0, 0])
    metrics_ax = fig.add_subplot(grid[1, 0])
    chart1_ax = fig.add_subplot(grid[2, 0])
    chart2_ax = fig.add_subplot(grid[3, 0])
    chart3_ax = fig.add_subplot(grid[4, 0])
    table_ax = fig.add_subplot(grid[5, 0])
    proscons_ax = fig.add_subplot(grid[6, 0])
    footer_ax = fig.add_subplot(grid[7, 0])

    _draw_header(header_ax, data)
    _draw_metrics_strip(metrics_ax, data["latest"])

    chart_specs = [
        ("Revenue & Profit Trend", charts.revenue_profit_trend, data["pnl"]),
        ("Return Metrics", charts.returns_trend, data["ratios"]),
        ("Cash Flow", charts.cashflow_trend, data["cashflow"]),
    ]

    for (title, builder, frame), slot_ax in zip(
        chart_specs, [chart1_ax, chart2_ax, chart3_ax]
    ):
        slot_ax.text(
            0.02,
            0.96,
            title,
            transform=slot_ax.transAxes,
            fontsize=11,
            fontweight="bold",
            color=NAVY,
            va="top",
        )

        chart_fig = builder(frame, ax=slot_ax)

        if chart_fig is None:
            slot_ax.text(
                0.5,
                0.4,
                "No data available",
                transform=slot_ax.transAxes,
                ha="center",
                va="center",
                fontsize=10,
                color=GREY,
            )

    _draw_history_table(table_ax, _history_table(data))
    _draw_pros_cons(proscons_ax, data["pros"], data["cons"])
    _draw_footer(footer_ax)

    output_path = os.path.join(output_dir, f"{company_id}_tearsheet.png")
    save_figure(fig, output_path)

    return output_path


# ==========================================================
# BATCH GENERATION
# ==========================================================

def generate_all_tearsheets(
    db_path: str = DB_PATH,
    output_dir: Optional[str] = None,
) -> List[str]:
    """Generate a tearsheet for every company in the universe.

    Returns the list of generated file paths.
    """
    if output_dir is None:
        output_dir = TEARSHEET_DIR

    companies = load_companies(db_path)
    validate_universe(companies)

    paths: List[str] = []
    company_ids = companies["company_id"].tolist()

    for index, company_id in enumerate(company_ids, start=1):
        path = generate_tearsheet(company_id, db_path, output_dir)
        paths.append(path)
        print(f"[{index}/{len(company_ids)}] {company_id} -> {path}")

    return paths


# ==========================================================
# ENTRY POINT
# ==========================================================

def main() -> None:
    print("Generating company tearsheets...")

    companies = load_companies()
    validate_universe(companies)

    print(f"Companies: {len(companies)}")

    paths = generate_all_tearsheets()

    print(f"Generated: {len(paths)} tearsheets")
    print(f"Directory: {TEARSHEET_DIR}")


if __name__ == "__main__":
    main()
