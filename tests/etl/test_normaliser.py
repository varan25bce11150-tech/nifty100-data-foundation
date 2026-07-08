import pytest

from src.etl.normaliser import (
    normalize_year,
    normalize_ticker,
)


def test_year_fy():
    assert normalize_year("FY2024") == 2024


def test_year_dash():
    assert normalize_year("2024-25") == 2024


def test_year_plain():
    assert normalize_year("2023") == 2023


def test_year_int():
    assert normalize_year(2022) == 2022


def test_year_none():
    assert normalize_year(None) is None


def test_year_invalid():
    assert normalize_year("ABC") is None


def test_ticker_caps():
    assert normalize_ticker("reliance") == "RELIANCE"


def test_ticker_space():
    assert normalize_ticker(" Reliance ") == "RELIANCE"


def test_ticker_dot():
    assert normalize_ticker("INFY.") == "INFY"


def test_ticker_comma():
    assert normalize_ticker("ABC,") == "ABC"


def test_ticker_amp():
    assert normalize_ticker("L&T") == "LANDT"


def test_ticker_none():
    assert normalize_ticker(None) is None