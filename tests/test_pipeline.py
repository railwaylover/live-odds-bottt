from bot import config
from bot.analysis import pipeline
from bot.feeds.base import LiveEvent, MarketPrice, OutcomePrice


def _ev(prob_home=0.55, market_home=2.2, corroborated=True, volume=500.0):
    ev = LiveEvent("e1", "nba", "A vs B", True,
                   [MarketPrice("moneyline", None,
                                [OutcomePrice("home", 1 / prob_home),
                                 OutcomePrice("away", 1 / (1 - prob_home))])])
    corroborating = []
    if corroborated:
        corroborating = [LiveEvent("x", "nba", "A vs B", True,
                                   [MarketPrice("moneyline", None,
                                                [OutcomePrice("home", market_home, volume),
                                                 OutcomePrice("away", 3.0, volume)])])]
    return ev, corroborating


def test_obvious_tier_when_big_edge():
    ev, cor = _ev(prob_home=0.7, market_home=2.0)
    sel = pipeline.evaluate(ev, cor)
    assert sel and sel["tier"] == "obvious"
    assert sel["thesis"] and sel["invalidation"]


def test_single_source_discarded():
    ev, _ = _ev(corroborated=False)
    assert pipeline.evaluate(ev, []) is None


def test_thin_volume_withheld():
    ev, cor = _ev(prob_home=0.7, market_home=2.0, volume=1.0)
    assert pipeline.evaluate(ev, cor) is None


def test_no_edge_discarded():
    ev, cor = _ev(prob_home=0.5, market_home=2.0)
    assert pipeline.evaluate(ev, cor) is None
