from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    interest_coverage_label,
    interest_coverage_warning,
    net_debt,
    asset_turnover,
)


def test_debt_to_equity_normal():
    assert debt_to_equity(100, 10, 390) == 0.25


def test_debt_to_equity_debt_free():
    assert debt_to_equity(0, 10, 390) == 0.0


def test_debt_to_equity_negative_equity():
    assert debt_to_equity(100, -50, 25) is None


def test_high_leverage_flag():
    assert high_leverage_flag(6.2, "IT") is True


def test_financial_sector_no_high_leverage():
    assert high_leverage_flag(6.2, "Banks") is False


def test_interest_coverage_ratio():
    assert interest_coverage_ratio(200, 20, 10) == 22.0


def test_interest_coverage_debt_free():
    assert interest_coverage_label(None) == "Debt Free"


def test_interest_coverage_warning():
    assert interest_coverage_warning(1.2) is True


def test_asset_turnover():
    assert asset_turnover(1000, 500) == 2.0


def test_asset_turnover_zero_assets():
    assert asset_turnover(1000, 0) is None


def test_net_debt():
    assert net_debt(500, 150) == 350