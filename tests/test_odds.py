import pytest

from bot.analysis import odds as O


def test_american_conversion():
    assert O.american_to_decimal(-110) == pytest.approx(1.9090, rel=1e-3)
    assert O.american_to_decimal(150) == pytest.approx(2.5)


def test_devig_normalizes():
    fair = O.devig([1.9, 1.9])
    assert sum(fair) == pytest.approx(1.0)
    assert fair[0] == pytest.approx(0.5)


def test_edge_and_ev_positive():
    assert O.edge(0.6, 2.0) == pytest.approx(0.1)
    assert O.expected_value(0.6, 2.0) == pytest.approx(0.2)


def test_kelly_lite_capped():
    assert O.kelly_lite(0.9, 10.0, 2.0) <= 2.0
    assert O.kelly_lite(0.1, 1.5, 1.0) == 0.0
