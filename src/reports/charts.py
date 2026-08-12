"""
Sprint 7 - Day 42
Report Charts

Reusable matplotlib chart builders shared by the tearsheet, sector and
portfolio summary reports.

Every builder:
- works on a per-company (or per-group) DataFrame;
- aggregates duplicate years to their mean before plotting;
- returns None when the input is empty, so callers can fall back to a
  "no data" note instead of crashing;
- accepts an optional target `ax`; when provided the chart is drawn into
  that axes (used by the multi-panel tearsheet), otherwise a fresh figure
  is created and returned.

Charts are deterministic: the same input always produces the same output.
"""

from __future__ import annotations

from typing import List, Optional

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.reports.styles import (
    CASHFLOW_COLORS,
    CHART_FIGSIZE,
    RETURN_COLORS,
    apply_chart_style,
)


# ==========================================================
# HELPERS
# ==========================================================

def _yearly_series(
    data: pd.DataFrame,
    value_column: str,
) -> pd.Series:
    """Aggregate a column to one mean value per calendar year.

    Returns an empty Series when the frame is empty or the column is
    entirely missing. Year rows without an extractable year are dropped.
    """
    if data is None or data.empty or value_column not in data.columns:
        return pd.Series(dtype=float)

    frame = data.copy()
    frame[value_column] = pd.to_numeric(frame[value_column], errors="coerce")
    frame = frame.dropna(subset=["calendar_year", value_column])

    if frame.empty:
        return pd.Series(dtype=float)

    return frame.groupby("calendar_year")[value_column].mean().sort_index()


def _numeric_years(data: pd.DataFrame, value_column: str) -> pd.DataFrame:
    """Return a year-indexed numeric DataFrame with NaN years dropped."""
    if data is None or data.empty or value_column not in data.columns:
        return pd.DataFrame()

    frame = data.copy()
    frame[value_column] = pd.to_numeric(frame[value_column], errors="coerce")
    frame = frame.dropna(subset=["calendar_year", value_column])

    if frame.empty:
        return pd.DataFrame()

    return frame.sort_values("calendar_year")


def _axes_or_new(figsize):
    """Return (fig, ax) using a fresh figure when no axes is provided."""
    fig, ax = plt.subplots(figsize=figsize)
    return fig, ax


# ==========================================================
# CHART BUILDERS
# ==========================================================

def revenue_profit_trend(
    pnl: pd.DataFrame,
    ax: Optional[plt.Axes] = None,
) -> Optional[plt.Figure]:
    """Bar chart of sales with an overlaid net-profit line by year.

    Returns None when no usable profit-and-loss data is available.
    """
    sales = _yearly_series(pnl, "sales")
    profit = _yearly_series(pnl, "net_profit")

    if sales.empty:
        return None

    fig, target = _axes_or_new(CHART_FIGSIZE) if ax is None else (ax.figure, ax)

    years = sales.index.astype(int).tolist()

    target.bar(years, sales.values, color="#1F77B4", alpha=0.75, label="Sales")
    target.set_xlabel("Year")
    target.set_ylabel("Amount (Cr)")
    target.set_title("Revenue & Net Profit Trend")

    if not profit.empty:
        profit_years = profit.index.astype(int).tolist()
        target.plot(
            profit_years,
            profit.values,
            color="#C0392B",
            marker="o",
            linewidth=2,
            label="Net Profit",
        )

    target.legend(loc="upper left")
    apply_chart_style(target)

    if ax is None:
        fig.tight_layout()

    return fig


def returns_trend(
    ratios: pd.DataFrame,
    ax: Optional[plt.Axes] = None,
) -> Optional[plt.Figure]:
    """Line chart of ROE / ROCE / ROA across the available years."""
    series: List[pd.Series] = []
    labels: List[str] = []

    for metric in ("return_on_equity_pct", "return_on_capital_employed_pct",
                   "return_on_assets_pct"):
        values = _yearly_series(ratios, metric)
        if not values.empty:
            series.append(values)
            labels.append(metric)

    if not series:
        return None

    fig, target = _axes_or_new(CHART_FIGSIZE) if ax is None else (ax.figure, ax)

    short_labels = {
        "return_on_equity_pct": "ROE",
        "return_on_capital_employed_pct": "ROCE",
        "return_on_assets_pct": "ROA",
    }

    for values, label in zip(series, labels):
        target.plot(
            values.index.astype(int).tolist(),
            values.values,
            color=RETURN_COLORS[label],
            marker="o",
            linewidth=2,
            label=short_labels[label],
        )

    target.set_xlabel("Year")
    target.set_ylabel("Percent (%)")
    target.set_title("Return Metrics Trend (ROE / ROCE / ROA)")
    target.legend(loc="best")
    apply_chart_style(target)

    if ax is None:
        fig.tight_layout()

    return fig


def cashflow_trend(
    cashflow: pd.DataFrame,
    ax: Optional[plt.Axes] = None,
) -> Optional[plt.Figure]:
    """Grouped bar chart of operating / investing / financing activity."""
    components = ["operating_activity", "investing_activity", "financing_activity"]

    frame = _numeric_years(cashflow, components[0])

    if frame.empty:
        return None

    frame = frame[["calendar_year"] + components].copy()
    for column in components:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    yearly = frame.groupby("calendar_year")[components].mean().sort_index()

    if yearly.empty:
        return None

    fig, target = _axes_or_new(CHART_FIGSIZE) if ax is None else (ax.figure, ax)

    years = yearly.index.astype(int).tolist()
    width = 0.25
    offsets = np.arange(len(years))

    for offset, column in enumerate(components):
        target.bar(
            offsets + (offset - 1) * width,
            yearly[column].values,
            width=width,
            color=CASHFLOW_COLORS[column],
            label=column.replace("_", " ").title(),
        )

    target.set_xticks(offsets)
    target.set_xticklabels(years)
    target.set_xlabel("Year")
    target.set_ylabel("Amount (Cr)")
    target.set_title("Cash Flow Components")
    target.legend(loc="best")
    apply_chart_style(target)

    if ax is None:
        fig.tight_layout()

    return fig


def margin_trend(
    ratios: pd.DataFrame,
    ax: Optional[plt.Axes] = None,
) -> Optional[plt.Figure]:
    """Line chart of operating and net profit margins across years."""
    series: List[pd.Series] = []
    labels: List[str] = []

    for metric in ("operating_profit_margin_pct", "net_profit_margin_pct"):
        values = _yearly_series(ratios, metric)
        if not values.empty:
            series.append(values)
            labels.append(metric)

    if not series:
        return None

    fig, target = _axes_or_new(CHART_FIGSIZE) if ax is None else (ax.figure, ax)

    for values, label in zip(series, labels):
        target.plot(
            values.index.astype(int).tolist(),
            values.values,
            marker="o",
            linewidth=2,
            label="OPM" if "operating" in label else "NPM",
        )

    target.set_xlabel("Year")
    target.set_ylabel("Percent (%)")
    target.set_title("Operating & Net Profit Margin Trend")
    target.legend(loc="best")
    apply_chart_style(target)

    if ax is None:
        fig.tight_layout()

    return fig


def quality_bar(
    data: pd.DataFrame,
    label_column: str,
    value_column: str,
    title: str,
    xlabel: str = "Score",
    ax: Optional[plt.Axes] = None,
) -> Optional[plt.Figure]:
    """Horizontal bar chart used to rank companies or sectors by a metric.

    Sorted descending so the best performer sits at the top.
    """
    if data is None or data.empty or value_column not in data.columns:
        return None

    frame = data.copy()
    frame[value_column] = pd.to_numeric(frame[value_column], errors="coerce")
    frame[label_column] = frame[label_column].fillna("Unknown").astype(str)
    frame = frame.dropna(subset=[value_column]).sort_values(
        value_column, ascending=True
    )

    if frame.empty:
        return None

    fig, target = _axes_or_new(CHART_FIGSIZE) if ax is None else (ax.figure, ax)

    target.barh(
        frame[label_column].tolist(),
        frame[value_column].values,
        color="#1F77B4",
        alpha=0.8,
    )
    target.set_xlabel(xlabel)
    target.set_title(title)

    target.grid(axis="x", alpha=0.3, linestyle="--")
    target.set_axisbelow(True)

    if ax is None:
        fig.tight_layout()

    return fig
