import logging

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    check_opm_difference,
)


def test_net_profit_margin_normal():
    assert net_profit_margin(100, 1000) == 10.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(100, 0) is None


def test_operating_profit_margin():
    assert operating_profit_margin(200, 1000) == 20.0


def test_return_on_equity_normal():
    assert return_on_equity(120, 10, 390) == 30.0


def test_return_on_equity_negative_equity():
    assert return_on_equity(120, -100, 50) is None


def test_return_on_capital_employed():
    assert return_on_capital_employed(
        operating_profit=200,
        interest=20,
        equity_capital=10,
        reserves=390,
        borrowings=100,
    ) == 44.0


def test_return_on_assets_zero_assets():
    assert return_on_assets(100, 0) is None


def test_opm_difference_detection(caplog):
    caplog.set_level(logging.WARNING)

    result = check_opm_difference(
        computed_opm=25.0,
        source_opm=20.0,
        company_id="TCS",
        year=2025,
    )

    assert result is True
    assert "OPM mismatch" in caplog.text