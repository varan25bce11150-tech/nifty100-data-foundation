"""
normaliser.py
Utility functions for cleaning and standardising incoming data.
"""

import re


def normalize_year(value):
    """
    Normalize different year formats into a 4-digit integer.

    Examples:
        FY2024   -> 2024
        2023-24  -> 2023
        2022     -> 2022
        2021     -> 2021
        None     -> None
        ABC      -> None
    """

    if value is None:
        return None

    value = str(value).strip()

    match = re.search(r"20\d{2}", value)

    if match:
        return int(match.group())

    return None


def normalize_ticker(value):
    """
    Normalize stock ticker symbols.

    Examples:
        infy         -> INFY
        infy.ns      -> INFY
        INFY EQ      -> INFY
        NSE:INFY     -> INFY
        INFY.        -> INFY
        INFY,        -> INFY
        L&T          -> LANDT
        None         -> None
    """

    if value is None:
        return None

    value = str(value).upper().strip()

    # Remove exchange prefix
    if ":" in value:
        value = value.split(":")[-1]

    # Remove common suffixes
    value = value.replace(".NS", "")
    value = value.replace(" EQ", "")

    # Replace ampersand with AND
    value = value.replace("&", "AND")

    # Remove punctuation
    value = value.replace(".", "")
    value = value.replace(",", "")

    # Remove all whitespace
    value = re.sub(r"\s+", "", value)

    return value