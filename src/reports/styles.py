"""
Sprint 7 - Day 42
Report Styling

Shared constants and formatting helpers for the generated financial
reports (tearsheets, sector reports and the portfolio summary).

Contents:
- Colour palette used across every generated chart.
- Indian-style number formatting helpers.
- Matplotlib axis styling used to keep every chart visually consistent.
"""

from __future__ import annotations

from typing import Optional, Union

import matplotlib.pyplot as plt


# ==========================================================
# COLOUR PALETTE
# ==========================================================

NAVY = "#0F2B46"
BLUE = "#1F77B4"
GREEN = "#2E8B57"
RED = "#C0392B"
AMBER = "#E67E22"
GREY = "#7F8C8D"
LIGHT_GREY = "#ECF0F1"

# Colours used for the three cash-flow components.
CASHFLOW_COLORS = {
    "operating_activity": GREEN,
    "investing_activity": RED,
    "financing_activity": AMBER,
}

# Colours used for the three return metrics.
RETURN_COLORS = {
    "return_on_equity_pct": BLUE,
    "return_on_capital_employed_pct": GREEN,
    "return_on_assets_pct": AMBER,
}

# ==========================================================
# LAYOUT CONSTANTS
# ==========================================================

CHART_FIGSIZE = (10, 5.5)
CHART_DPI = 150
HEADER_BG = NAVY


# ==========================================================
# NUMBER FORMATTING
# ==========================================================

def _indian_grouping(value: Union[int, float]) -> str:
    """Group the integer part of a number using Indian digit grouping.

    Indian convention groups the last three digits, then every two:
        1234567.89 -> "12,34,567.89"

    The grouping is applied to the absolute value; the sign is preserved.
    """
    sign = "-" if value < 0 else ""
    absolute = abs(value)

    integer_part = int(absolute)
    # Format through a string so floating-point noise never leaks in.
    fraction = f"{absolute:.2f}".split(".")[1]

    digits = str(integer_part)

    if len(digits) <= 3:
        grouped = digits
    else:
        head = digits[:-3]
        tail = digits[-3:]

        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)

        grouped = ",".join(parts) + "," + tail

    return f"{sign}{grouped}.{fraction}"


def format_cr(value: Optional[float], decimals: int = 2) -> str:
    """Format a value in crore with Indian digit grouping.

    Examples:
        format_cr(1234567.891)  -> "12,34,567.89 Cr"
        format_cr(None)         -> "N/A"
    """
    if value is None or value != value:  # NaN guard
        return "N/A"

    return f"{_indian_grouping(float(value))} Cr"


def format_number(value: Optional[float], decimals: int = 2) -> str:
    """Format a plain number with Indian digit grouping.

    Examples:
        format_number(1234567.891) -> "12,34,567.89"
        format_number(None)        -> "N/A"
    """
    if value is None or value != value:  # NaN guard
        return "N/A"

    return _indian_grouping(round(float(value), decimals))


def format_percent(value: Optional[float], decimals: int = 1) -> str:
    """Format a percentage value.

    Examples:
        format_percent(18.346) -> "18.3%"
        format_percent(None)   -> "N/A"
    """
    if value is None or value != value:  # NaN guard
        return "N/A"

    return f"{float(value):.{decimals}f}%"


def format_ratio(value: Optional[float], decimals: int = 2) -> str:
    """Format a unitless ratio.

    Examples:
        format_ratio(0.4567) -> "0.46"
        format_ratio(None)   -> "N/A"
    """
    if value is None or value != value:  # NaN guard
        return "N/A"

    return f"{float(value):.{decimals}f}"


# ==========================================================
# MATPLOTLIB STYLING
# ==========================================================

def apply_chart_style(ax: plt.Axes) -> None:
    """Apply the standard visual style to a matplotlib axes object.

    Removes the top/right spines and adds a light horizontal grid so
    every report chart looks consistent. Layout (tight_layout) is handled
    by `save_figure`, which keeps multi-panel figures intact.
    """
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    ax.tick_params(axis="x", rotation=45)


def save_figure(fig: plt.Figure, path: str, dpi: int = CHART_DPI) -> str:
    """Save a matplotlib figure to disk and close it.

    Standalone charts call `tight_layout` themselves before returning;
    multi-panel figures (e.g. the tearsheet) control their own layout via
    gridspec, so no global layout pass is applied here.

    Returns the path the figure was written to.
    """
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path
