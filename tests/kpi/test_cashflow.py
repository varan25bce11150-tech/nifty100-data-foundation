from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_pat_ratio,
    cfo_quality_score,
    capex_intensity,
    capex_label,
    fcf_conversion_rate,
    capital_allocation_pattern,
)


def test_free_cash_flow():
    assert free_cash_flow(100, -40) == 60


def test_cfo_pat_ratio():
    assert cfo_pat_ratio(120, 100) == 1.2


def test_cfo_pat_zero():
    assert cfo_pat_ratio(100, 0) is None


def test_cfo_quality():
    assert cfo_quality_score(120, 100) == "High Quality"


def test_capex_intensity():
    assert capex_intensity(-50, 1000) == 5.0


def test_capex_label():
    assert capex_label(-50, 1000) == "Moderate"


def test_fcf_conversion():
    assert fcf_conversion_rate(100, -40, 200) == 30.0


def test_capital_allocation():
    pattern, cfo, cfi, cff = capital_allocation_pattern(
        100,
        -50,
        -20,
        80,
    )

    assert pattern == "Shareholder Returns"
    assert cfo == "+"
    assert cfi == "-"
    assert cff == "-"