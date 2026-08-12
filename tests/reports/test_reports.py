"""Unit and integration tests for the Sprint 7 report generators."""

import os

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from src.reports import charts
from src.reports.data import (
    DB_PATH,
    EXPECTED_COMPANY_COUNT,
    load_cluster_labels,
    load_companies,
    load_latest_snapshot,
    load_sector_names,
    validate_universe,
)
from src.reports.portfolio_summary import (
    build_summary_dataframe,
    generate_portfolio_summary,
    validate_outputs,
)
from src.reports.sector_report import (
    _build_sector_data,
    _slug,
    generate_sector_report,
)
from src.reports.styles import (
    _indian_grouping,
    format_cr,
    format_number,
    format_percent,
    format_ratio,
)
from src.reports.tearsheet import (
    _build_tearsheet_data,
    _history_table,
    _truncate,
    generate_tearsheet,
)


# ==========================================================
# styles
# ==========================================================

def test_indian_grouping():
    assert _indian_grouping(999) == "999.00"
    assert _indian_grouping(1234567.89) == "12,34,567.89"
    assert _indian_grouping(-1234567) == "-12,34,567.00"


def test_format_cr():
    assert format_cr(1234567.891) == "12,34,567.89 Cr"
    assert format_cr(None) == "N/A"
    assert format_cr(float("nan")) == "N/A"


def test_format_percent():
    assert format_percent(18.346) == "18.3%"
    assert format_percent(0) == "0.0%"
    assert format_percent(None) == "N/A"


def test_format_number():
    assert format_number(1234567.891) == "12,34,567.89"
    assert format_number(None) == "N/A"


def test_format_ratio():
    assert format_ratio(0.4567) == "0.46"
    assert format_ratio(None) == "N/A"


# ==========================================================
# charts
# ==========================================================

def _year_frame(years, sales):
    return pd.DataFrame({
        "company_id": ["A"] * len(years),
        "year": years,
        "sales": sales,
    })


def test_yearly_series_text_years():
    frame = _year_frame(
        [f"Mar {y}" for y in range(2019, 2024)],
        [100.0, 110.0, 120.0, 130.0, 140.0],
    )
    frame["calendar_year"] = frame["year"].apply(
        lambda v: int(str(v).split()[-1])
    )

    series = charts._yearly_series(frame, "sales")

    assert list(series.index) == [2019, 2020, 2021, 2022, 2023]
    assert series.loc[2023] == 140.0


def test_yearly_series_empty():
    assert charts._yearly_series(pd.DataFrame(), "sales").empty
    assert charts._yearly_series(
        pd.DataFrame({"calendar_year": [2020], "sales": [np.nan]}),
        "sales",
    ).empty


def test_revenue_profit_trend_none_on_empty():
    assert charts.revenue_profit_trend(pd.DataFrame()) is None


def test_revenue_profit_trend_returns_fig():
    frame = _year_frame(
        [f"Mar {y}" for y in range(2019, 2024)],
        [100.0, 110.0, 120.0, 130.0, 140.0],
    )
    frame["calendar_year"] = frame["year"].apply(
        lambda v: int(str(v).split()[-1])
    )
    frame["net_profit"] = [10.0, 11.0, 12.0, 13.0, 14.0]

    fig = charts.revenue_profit_trend(frame)
    assert fig is not None
    plt.close(fig)


def test_returns_trend_returns_fig():
    frame = pd.DataFrame({
        "calendar_year": [2019, 2020, 2021],
        "return_on_equity_pct": [10.0, 12.0, 14.0],
        "return_on_capital_employed_pct": [15.0, 16.0, 17.0],
        "return_on_assets_pct": [5.0, 6.0, 7.0],
    })

    fig = charts.returns_trend(frame)
    assert fig is not None
    plt.close(fig)


def test_returns_trend_none_without_data():
    assert charts.returns_trend(pd.DataFrame()) is None


def test_cashflow_trend_none_on_empty():
    assert charts.cashflow_trend(pd.DataFrame()) is None


def test_quality_bar_draws_into_provided_ax():
    data = pd.DataFrame({
        "name": ["A", "B", "C"],
        "score": [10.0, 20.0, 30.0],
    })

    fig = plt.figure()
    ax = fig.add_subplot(111)

    result = charts.quality_bar(data, "name", "score", "Test", ax=ax)

    assert result is fig
    assert len(ax.patches) == 3
    plt.close(fig)


def test_quality_bar_none_on_empty():
    assert charts.quality_bar(pd.DataFrame(), "name", "score", "Test") is None


# ==========================================================
# data layer
# ==========================================================

def test_load_companies_universe():
    companies = load_companies()

    assert len(companies) == EXPECTED_COMPANY_COUNT
    assert companies["company_id"].is_unique
    assert companies["company_name"].str.len().min() > 0  # stripped names


def test_load_latest_snapshot():
    snapshot = load_latest_snapshot()

    assert len(snapshot) == EXPECTED_COMPANY_COUNT
    assert snapshot["company_id"].is_unique

    # SBIN has no financial_ratios -> latest ratios stay NaN.
    sbin = snapshot[snapshot["company_id"] == "SBIN"].iloc[0]
    assert pd.isna(sbin["return_on_equity_pct"])

    # Every company has market-cap data.
    assert snapshot["market_cap"].notna().sum() == EXPECTED_COMPANY_COUNT


def test_load_sector_names():
    sectors = load_sector_names()

    assert len(sectors) == 10
    assert "Financials" in sectors


def test_validate_universe_raises_on_wrong_count():
    data = pd.DataFrame({"company_id": [f"C{i}" for i in range(10)]})

    with pytest.raises(ValueError):
        validate_universe(data)


def test_validate_universe_raises_on_duplicates():
    data = pd.DataFrame({"company_id": ["A", "A"] * 46})

    with pytest.raises(ValueError):
        validate_universe(data)


def test_load_cluster_labels_missing_file():
    frame = load_cluster_labels(cluster_label_file="does_not_exist.csv")

    assert frame.empty
    assert list(frame.columns) == ["company_id", "cluster_id", "cluster_name"]


# ==========================================================
# tearsheet
# ==========================================================

def test_build_tearsheet_data_known_company():
    data = _build_tearsheet_data("RELIANCE")

    assert data["company_id"] == "RELIANCE"
    assert data["company_name"]
    assert data["broad_sector"]
    assert data["industry"]
    assert set(data.keys()) >= {
        "company_id",
        "company_name",
        "broad_sector",
        "industry",
        "ratios",
        "pnl",
        "cashflow",
        "pros",
        "cons",
        "latest",
    }


def test_build_tearsheet_data_unknown_company_raises():
    with pytest.raises(ValueError):
        _build_tearsheet_data("NOT-A-COMPANY")


def test_build_tearsheet_data_sbin_missing_ratios():
    data = _build_tearsheet_data("SBIN")

    # SBIN has no financial_ratios rows: latest values must be NaN-safe.
    assert pd.isna(data["latest"]["return_on_equity_pct"])
    assert pd.isna(data["latest"]["composite_quality_score"])
    assert data["ratios"].empty


def test_history_table_sorted_desc():
    data = _build_tearsheet_data("RELIANCE")

    table = _history_table(data)

    assert not table.empty
    years = table["calendar_year"].dropna().tolist()
    assert years == sorted(years, reverse=True)
    assert len(table) <= 8


def test_truncate():
    assert _truncate(None) == "N/A"
    assert _truncate("short") == "short"
    assert _truncate("x" * 1000, limit=20).endswith("...")
    assert len(_truncate("x" * 1000, limit=20)) <= 20


def test_generate_tearsheet_writes_file(tmp_path):
    path = generate_tearsheet("RELIANCE", output_dir=str(tmp_path))

    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    assert path.endswith("RELIANCE_tearsheet.png")


# ==========================================================
# sector report
# ==========================================================

def test_slug():
    assert _slug("Consumer Discretionary") == "consumer_discretionary"
    assert _slug("Information Technology") == "information_technology"
    assert _slug("Financials") == "financials"


def test_build_sector_data_known_sector():
    data = _build_sector_data("Financials")

    assert data["company_count"] > 0
    assert data["sector"] == "Financials"
    assert len(data["companies"]) == data["company_count"]
    assert data["total_market_cap"] >= 0


def test_build_sector_data_unknown_sector_raises():
    with pytest.raises(ValueError):
        _build_sector_data("Not A Real Sector")


def test_generate_sector_report_writes_file(tmp_path):
    path = generate_sector_report("Financials", output_dir=str(tmp_path))

    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    assert path.endswith("financials_report.png")


# ==========================================================
# portfolio summary
# ==========================================================

def test_build_summary_dataframe():
    summary = build_summary_dataframe()

    assert len(summary) == EXPECTED_COMPANY_COUNT
    assert summary["company_id"].is_unique
    assert "cluster_name" in summary.columns
    assert "composite_quality_score" in summary.columns


def test_generate_portfolio_summary(tmp_path):
    png_path, csv_path = generate_portfolio_summary(
        report_dir=str(tmp_path),
        csv_dir=str(tmp_path),
    )

    assert os.path.exists(png_path)
    assert os.path.getsize(png_path) > 0
    assert os.path.exists(csv_path)

    summary = pd.read_csv(csv_path)
    assert len(summary) == EXPECTED_COMPANY_COUNT
    assert summary["company_id"].nunique() == EXPECTED_COMPANY_COUNT

    checks = validate_outputs(png_path, csv_path)
    assert all(checks.values())


def test_validate_outputs_detects_missing_csv(tmp_path):
    checks = validate_outputs(
        os.path.join(str(tmp_path), "missing.png"),
        os.path.join(str(tmp_path), "missing.csv"),
    )

    assert checks["PNG exists"] is False
    assert checks["CSV exists"] is False
    assert checks["CSV rows = 92"] is False
