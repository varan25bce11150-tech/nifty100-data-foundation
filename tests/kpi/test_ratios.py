"""
KPI Tests - Profitability & Leverage Ratios

Tests:
- Net Profit Margin
- Operating Profit Margin
- ROE
- ROCE
- ROA
- Debt to Equity
- Interest Coverage
- Asset Turnover
"""

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover,
)


# ============================================================
# Profitability Ratio Tests
# ============================================================


def test_net_profit_margin():

    result = net_profit_margin(
        net_profit=200,
        sales=1000
    )

    assert result == 20.0



def test_operating_profit_margin():

    result = operating_profit_margin(
        operating_profit=300,
        sales=1000
    )

    assert result == 30.0



def test_return_on_equity():

    result = return_on_equity(
        net_profit=200,
        equity_capital=500,
        reserves=500
    )

    assert result == 20.0



def test_return_on_capital_employed():

    result = return_on_capital_employed(
        operating_profit=300,
        interest=50,
        equity_capital=500,
        reserves=500,
        borrowings=500
    )

    # EBIT = 350
    # Capital = 1500
    # ROCE = 23.33%

    assert result == 23.33



def test_return_on_assets():

    result = return_on_assets(
        net_profit=200,
        total_assets=2000
    )

    assert result == 10.0



# ============================================================
# Leverage Ratio Tests
# ============================================================


def test_debt_to_equity():

    result = debt_to_equity(
        borrowings=1000,
        equity_capital=500,
        reserves=500
    )

    assert result == 1.0



def test_debt_free_company():

    result = debt_to_equity(
        borrowings=0,
        equity_capital=500,
        reserves=500
    )

    assert result == 0.0



# ============================================================
# Efficiency Ratio Tests
# ============================================================


def test_interest_coverage_ratio():

    result = interest_coverage_ratio(
        operating_profit=500,
        other_income=100,
        interest=100
    )

    assert result == 6.0



def test_asset_turnover():

    result = asset_turnover(
        sales=1000,
        total_assets=500
    )

    assert result == 2.0



# ============================================================
# Edge Case Tests
# ============================================================


def test_zero_sales_returns_none():

    result = net_profit_margin(
        net_profit=100,
        sales=0
    )

    assert result is None



def test_negative_equity_returns_none():

    result = return_on_equity(
        net_profit=100,
        equity_capital=-500,
        reserves=0
    )

    assert result is None


def test_interest_coverage_zero_interest():

    from src.analytics.ratios import interest_coverage_ratio

    result = interest_coverage_ratio(
        operating_profit=500,
        other_income=100,
        interest=0
    )

    assert result is None



def test_interest_coverage_label():

    from src.analytics.ratios import interest_coverage_label

    result = interest_coverage_label(None)

    assert result == "Debt Free"



def test_high_leverage_flag():

    from src.analytics.ratios import high_leverage_flag

    result = high_leverage_flag(
        debt_to_equity_ratio=6,
        sector="Manufacturing"
    )

    assert result is True



def test_financial_sector_no_high_leverage_flag():

    from src.analytics.ratios import high_leverage_flag

    result = high_leverage_flag(
        debt_to_equity_ratio=8,
        sector="Banking"
    )

    assert result is False    