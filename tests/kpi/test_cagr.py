from src.analytics.cagr import (
    calculate_cagr,
    CAGRFlag,
)


def test_normal_cagr():
    value, flag = calculate_cagr(100, 200, 5)

    assert round(value, 2) == 14.87
    assert flag == CAGRFlag.NORMAL


def test_decline_to_loss():
    value, flag = calculate_cagr(100, -50, 5)

    assert value is None
    assert flag == CAGRFlag.DECLINE_TO_LOSS


def test_turnaround():
    value, flag = calculate_cagr(-100, 50, 5)

    assert value is None
    assert flag == CAGRFlag.TURNAROUND


def test_both_negative():
    value, flag = calculate_cagr(-100, -50, 5)

    assert value is None
    assert flag == CAGRFlag.BOTH_NEGATIVE


def test_zero_base():
    value, flag = calculate_cagr(0, 50, 5)

    assert value is None
    assert flag == CAGRFlag.ZERO_BASE


def test_insufficient():
    value, flag = calculate_cagr(100, 200, 0)

    assert value is None
    assert flag == CAGRFlag.INSUFFICIENT


def test_revenue_growth():
    value, _ = calculate_cagr(500, 1000, 5)

    assert value > 0


def test_pat_growth():
    value, _ = calculate_cagr(50, 100, 5)

    assert value > 0


def test_eps_growth():
    value, _ = calculate_cagr(10, 20, 5)

    assert value > 0


def test_same_value():
    value, flag = calculate_cagr(100, 100, 5)

    assert value == 0
    assert flag == CAGRFlag.NORMAL