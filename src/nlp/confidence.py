"""
Sprint 5
Confidence Scoring Engine
"""

from __future__ import annotations

from typing import Optional


def clamp(score: float) -> int:
    """
    Clamp confidence score to 0-100.
    """
    if score < 0:
        return 0

    if score > 100:
        return 100

    return int(round(score))


def score_from_threshold(
    value: float,
    threshold: float,
    higher_is_better: bool = True,
    max_bonus: float = 25,
) -> int:
    """
    Generic threshold confidence.

    Example:
        ROE 28 vs threshold 20
        confidence increases with margin.
    """

    base = 60

    if higher_is_better:
        diff = value - threshold
    else:
        diff = threshold - value

    if diff <= 0:
        return 0

    bonus = min(diff * 2, max_bonus)

    return clamp(base + bonus)


def score_from_years(
    years: int,
    max_years: int = 10,
) -> int:
    """
    More years = stronger confidence.
    """

    years = max(0, min(years, max_years))

    return clamp(50 + years * 5)


def score_combined(
    threshold_score: int,
    persistence_years: int = 0,
    latest_year_bonus: bool = False,
) -> int:
    """
    Combines threshold score with persistence.
    """

    score = threshold_score

    score += min(persistence_years * 4, 20)

    if latest_year_bonus:
        score += 10

    return clamp(score)


def fixed(score: int) -> int:
    """
    Returns fixed confidence.
    """

    return clamp(score)


def average(*scores: Optional[int]) -> int:
    """
    Average of multiple confidence scores.
    """

    valid = [s for s in scores if s is not None]

    if not valid:
        return 0

    return clamp(sum(valid) / len(valid))