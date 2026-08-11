"""Unit and integration tests for the Sprint 6 clustering engine."""

import os

import numpy as np
import pandas as pd
import pytest

from src.analytics.clustering import (
    CLUSTER_LABEL_FILE,
    CLUSTER_PROFILE_FILE,
    ELBOW_FILE,
    FEATURE_COLUMNS,
    assign_cluster_names,
    calculate_fcf_cagr,
    calculate_revenue_cagr,
    extract_year,
    impute_sector_medians,
    make_unique_cluster_names,
    run,
    validate_results,
    winsorize_features,
)


# ==========================================================
# extract_year
# ==========================================================

def test_extract_year_full_month_year():
    assert extract_year("Mar 2024") == 2024
    assert extract_year("Dec 2023") == 2023
    assert extract_year("Jun 2022") == 2022


def test_extract_year_integer_and_float():
    assert extract_year(2024) == 2024
    assert extract_year(2024.0) == 2024
    assert extract_year("2024") == 2024


def test_extract_year_two_digit_suffix():
    assert extract_year("Mar-13") == 2013
    assert extract_year("Mar-24") == 2024


def test_extract_year_ttm_is_none():
    assert extract_year("TTM") is None


def test_extract_year_missing_and_invalid():
    assert extract_year(None) is None
    assert extract_year(np.nan) is None
    assert extract_year("") is None
    assert extract_year("not a year") is None
    assert extract_year("garbage-99") == 1999  # 2-digit fallback still safe


# ==========================================================
# Revenue CAGR
# ==========================================================

def _pl_frame(company_id, years, sales):
    return pd.DataFrame({
        "company_id": [company_id] * len(years),
        "year": years,
        "sales": sales,
    })


def test_revenue_cagr_normal():
    df = _pl_frame(
        "A",
        [f"Mar {y}" for y in range(2019, 2025)],
        [100.0, 110.0, 120.0, 130.0, 145.0, 161.0],
    )
    result = calculate_revenue_cagr(df)

    assert len(result) == 1
    assert result.iloc[0]["company_id"] == "A"
    # ((161 / 100) ** (1 / 5) - 1) * 100 ~= 10.0
    assert result.iloc[0]["revenue_cagr_5yr"] == pytest.approx(10.0, abs=0.1)


def test_revenue_cagr_ignores_ttm_and_short_history():
    df = pd.concat([
        _pl_frame(
            "A",
            [f"Mar {y}" for y in range(2019, 2025)] + ["TTM"],
            [100.0, 110.0, 120.0, 130.0, 145.0, 161.0, 999.0],
        ),
        _pl_frame(
            "B",
            [f"Mar {y}" for y in range(2020, 2025)],
            [100.0, 110.0, 120.0, 130.0, 140.0],
        ),
    ])

    result = calculate_revenue_cagr(df)

    # B has no beginning year exactly 5 years earlier -> excluded.
    assert set(result["company_id"]) == {"A"}
    assert result.iloc[0]["revenue_cagr_5yr"] == pytest.approx(10.0, abs=0.1)


def test_revenue_cagr_zero_or_negative_start_sales():
    years = [f"Mar {y}" for y in range(2019, 2025)]

    zero_start = _pl_frame("A", years, [0.0, 50.0, 60.0, 70.0, 80.0, 90.0])
    assert calculate_revenue_cagr(zero_start).empty

    negative_start = _pl_frame("A", years, [-100.0, 50.0, 60.0, 70.0, 80.0, 90.0])
    assert calculate_revenue_cagr(negative_start).empty


def test_revenue_cagr_negative_end_sales():
    df = _pl_frame(
        "A",
        [f"Mar {y}" for y in range(2019, 2025)],
        [100.0, 110.0, 120.0, 130.0, 140.0, -50.0],
    )
    assert calculate_revenue_cagr(df).empty


# ==========================================================
# FCF CAGR
# ==========================================================

def _cf_frame(company_id, years, operating, investing):
    return pd.DataFrame({
        "company_id": [company_id] * len(years),
        "year": years,
        "operating_activity": operating,
        "investing_activity": investing,
    })


def test_fcf_cagr_normal():
    df = _cf_frame(
        "A",
        [f"Mar {y}" for y in range(2019, 2025)],
        [120.0, 130.0, 140.0, 150.0, 160.0, 181.0],
        [-20.0] * 6,
    )
    result = calculate_fcf_cagr(df)

    assert len(result) == 1
    assert result.iloc[0]["company_id"] == "A"
    # FCF: 100, 110, 120, 130, 140, 161 -> CAGR ~= 10.0
    assert result.iloc[0]["fcf_cagr_5yr"] == pytest.approx(10.0, abs=0.1)


def test_fcf_cagr_negative_start_fcf():
    years = [f"Mar {y}" for y in range(2019, 2025)]
    df = _cf_frame(
        "A",
        years,
        [50.0, 60.0, 70.0, 80.0, 90.0, 100.0],
        [-100.0, -20.0, -20.0, -20.0, -20.0, -20.0],
    )
    # Beginning FCF = -50 -> CAGR not meaningful -> excluded.
    assert calculate_fcf_cagr(df).empty


def test_fcf_cagr_zero_start_fcf():
    years = [f"Mar {y}" for y in range(2019, 2025)]
    df = _cf_frame(
        "A",
        years,
        [20.0, 60.0, 70.0, 80.0, 90.0, 100.0],
        [-20.0] * 6,
    )
    # Beginning FCF = 0 -> excluded.
    assert calculate_fcf_cagr(df).empty


def test_fcf_cagr_negative_end_fcf():
    years = [f"Mar {y}" for y in range(2019, 2025)]
    df = _cf_frame(
        "A",
        years,
        [120.0, 130.0, 140.0, 150.0, 160.0, 100.0],
        [-20.0, -20.0, -20.0, -20.0, -20.0, -190.0],
    )
    # Ending FCF = -90 -> excluded instead of a meaningless CAGR.
    assert calculate_fcf_cagr(df).empty


def test_fcf_cagr_ignores_ttm():
    df = _cf_frame(
        "A",
        [f"Mar {y}" for y in range(2019, 2025)] + ["TTM"],
        [120.0, 130.0, 140.0, 150.0, 160.0, 181.0, 500.0],
        [-20.0] * 7,
    )
    result = calculate_fcf_cagr(df)

    assert len(result) == 1
    assert result.iloc[0]["fcf_cagr_5yr"] == pytest.approx(10.0, abs=0.1)


def test_fcf_cagr_two_digit_years():
    df = _cf_frame(
        "A",
        [f"Mar-{y}" for y in range(13, 19)],
        [120.0, 130.0, 140.0, 150.0, 160.0, 181.0],
        [-20.0] * 6,
    )
    result = calculate_fcf_cagr(df)

    assert len(result) == 1
    assert result.iloc[0]["fcf_cagr_5yr"] == pytest.approx(10.0, abs=0.1)


# ==========================================================
# Sector median imputation
# ==========================================================

def test_impute_sector_medians_sector_then_global():
    df = pd.DataFrame({
        "company_id": ["A", "B", "C", "D"],
        "broad_sector": ["Tech", "Tech", "Bank", "Bank"],
        "return_on_equity_pct": [10.0, np.nan, 20.0, np.nan],
        "debt_to_equity": [0.5, 0.5, np.nan, np.nan],
        "revenue_cagr_5yr": [5.0, 7.0, 9.0, 11.0],
        "fcf_cagr_5yr": [1.0, 2.0, 3.0, 4.0],
        "operating_profit_margin_pct": [10.0, 10.0, 20.0, 20.0],
    })

    result = impute_sector_medians(df)

    assert result[FEATURE_COLUMNS].isna().sum().sum() == 0
    # Missing ROE filled with the company's own sector median.
    assert result.loc[1, "return_on_equity_pct"] == 10.0  # Tech median
    assert result.loc[3, "return_on_equity_pct"] == 20.0  # Bank median
    # Entire sector missing -> global median fallback.
    assert result.loc[3, "debt_to_equity"] == 0.5
    # Non-missing values are untouched.
    assert result.loc[0, "return_on_equity_pct"] == 10.0
    assert result.loc[2, "debt_to_equity"] == 0.5


def test_impute_sector_medians_no_missing_input():
    df = pd.DataFrame({
        "company_id": ["A", "B"],
        "broad_sector": ["Tech", "Tech"],
        **{feature: [5.0, 6.0] for feature in FEATURE_COLUMNS},
    })
    result = impute_sector_medians(df)
    pd.testing.assert_frame_equal(result[FEATURE_COLUMNS], df[FEATURE_COLUMNS])


# ==========================================================
# Winsorization
# ==========================================================

def _winsor_frame():
    return pd.DataFrame({
        "company_id": [str(i) for i in range(10)],
        "return_on_equity_pct": [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 4379.0],
        "debt_to_equity": [0.1] * 9 + [50.0],
        "revenue_cagr_5yr": [10.0] * 10,
        "fcf_cagr_5yr": [10.0] * 10,
        "operating_profit_margin_pct": [20.0] * 10,
    })


def test_winsorize_extreme_outliers():
    result = winsorize_features(_winsor_frame())

    assert result["return_on_equity_pct"].max() < 4379.0
    assert result["debt_to_equity"].max() < 50.0
    assert result[FEATURE_COLUMNS].isna().sum().sum() == 0
    assert len(result) == 10  # no companies deleted


def test_winsorize_deterministic():
    first = winsorize_features(_winsor_frame())
    second = winsorize_features(_winsor_frame())
    pd.testing.assert_frame_equal(first, second)


# ==========================================================
# Cluster naming
# ==========================================================

def _profile_frame():
    return pd.DataFrame(
        [
            (0, 15.0, 0.5, 10.0, -5.0, 20.0),   # Low Growth / Core
            (1, 16.0, 6.0, 17.0, -3.0, 50.0),   # Leveraged Growth
            (2, 60.0, 0.8, 12.0, 25.0, 30.0),   # High ROE Compounders
            (3, 22.0, 0.5, 12.0, 33.0, 22.0),   # FCF Growth Leaders
            (4, 15.0, 0.2, 13.0, 20.0, 80.0),   # High-Margin Businesses
        ],
        columns=["cluster_id"] + FEATURE_COLUMNS,
    )


def test_assign_cluster_names_by_profile():
    names = assign_cluster_names(_profile_frame())

    assert names == {
        0: "Low Growth / Core",
        1: "Leveraged Growth",
        2: "High ROE Compounders",
        3: "FCF Growth Leaders",
        4: "High-Margin Businesses",
    }


def test_cluster_names_unique():
    names = assign_cluster_names(_profile_frame())
    assert len(set(names.values())) == 5


def test_cluster_names_fallback_balanced():
    df = pd.DataFrame(
        [
            (0, 15.0, 0.4, 10.0, 5.0, 25.0),
            (1, 16.0, 0.5, 11.0, 6.0, 26.0),
            (2, 14.0, 0.6, 9.0, 4.0, 24.0),
        ],
        columns=["cluster_id"] + FEATURE_COLUMNS,
    )
    names = make_unique_cluster_names(assign_cluster_names(df))

    assert "Balanced / Core" in names.values()
    assert len(set(names.values())) == 3


# ==========================================================
# Validation
# ==========================================================

def _valid_frames():
    company_ids = [f"C{i:02d}" for i in range(92)]
    data = pd.DataFrame({
        "company_id": company_ids,
        **{feature: [10.0] * 92 for feature in FEATURE_COLUMNS},
    })
    output = pd.DataFrame({
        "company_id": company_ids,
        "cluster_id": [i % 5 for i in range(92)],
        "cluster_name": ["Balanced / Core"] * 92,
        "distance_from_centroid": [1.2345] * 92,
    })
    profiles = pd.DataFrame({
        "cluster_id": list(range(5)),
        "company_count": [18, 19, 20, 17, 18],
        **{feature: [10.0] * 5 for feature in FEATURE_COLUMNS},
        "cluster_name": ["Balanced / Core"] * 5,
    })
    return data, output, profiles


def test_validate_results_passes():
    data, output, profiles = _valid_frames()
    checks = validate_results(data, output, profiles)
    assert all(checks.values())


def test_validate_results_detects_invalid_distance():
    data, output, profiles = _valid_frames()
    output.loc[0, "distance_from_centroid"] = np.nan
    checks = validate_results(data, output, profiles)
    assert checks["Invalid distances = 0"] is False


def test_validate_results_detects_wrong_row_count():
    data, output, profiles = _valid_frames()
    output = output.iloc[:91]
    checks = validate_results(data, output, profiles)
    assert checks["cluster_labels rows = 92"] is False


# ==========================================================
# Full pipeline
# ==========================================================

def test_full_pipeline():
    output = run()

    assert len(output) == 92
    assert output["company_id"].is_unique
    assert output["cluster_id"].nunique() == 5
    assert output["cluster_name"].notna().all()
    assert len(output["cluster_name"].unique()) == 5
    assert bool(np.isfinite(output["distance_from_centroid"].to_numpy(dtype=float)).all())

    assert os.path.exists(CLUSTER_LABEL_FILE)
    assert os.path.exists(CLUSTER_PROFILE_FILE)
    assert os.path.exists(ELBOW_FILE)

    labels = pd.read_csv(CLUSTER_LABEL_FILE)
    profiles = pd.read_csv(CLUSTER_PROFILE_FILE)

    assert len(labels) == 92
    assert len(profiles) == 5
