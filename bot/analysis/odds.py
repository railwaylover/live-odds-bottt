"""Odds math: conversion, de-vigging, edge/EV, Kelly-lite stake caps."""
from __future__ import annotations


def american_to_decimal(odds: float) -> float:
    odds = float(odds)
    if odds > 0:
        return 1 + odds / 100
    return 1 + 100 / abs(odds)


def decimal_to_prob(decimal_odds: float) -> float:
    return 1 / float(decimal_odds)


def prob_to_decimal(prob: float) -> float:
    return 1 / float(prob)


def devig(decimal_odds: list[float]) -> list[float]:
    """Remove overround by normalizing implied probabilities (multiplicative)."""
    implied = [decimal_to_prob(o) for o in decimal_odds]
    total = sum(implied)
    if total <= 0:
        raise ValueError("invalid odds for de-vigging")
    return [p / total for p in implied]


def edge(fair_prob: float, market_decimal: float) -> float:
    """Edge of a price vs fair probability: fair - implied."""
    return fair_prob - decimal_to_prob(market_decimal)


def expected_value(fair_prob: float, market_decimal: float) -> float:
    """EV per unit staked."""
    return fair_prob * market_decimal - 1


def kelly_fraction(fair_prob: float, market_decimal: float) -> float:
    b = market_decimal - 1
    if b <= 0:
        return 0.0
    q = 1 - fair_prob
    f = (b * fair_prob - q) / b
    return max(0.0, f)


def kelly_lite(fair_prob: float, market_decimal: float, cap: float) -> float:
    """Half-Kelly stake suggestion bounded by the tier cap."""
    return round(min(kelly_fraction(fair_prob, market_decimal) / 2, cap), 2)
