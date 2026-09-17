import tempfile

from bot.settle import settle
from bot.store import Store


def _store():
    return Store(path=tempfile.mktemp(suffix=".db"))


def test_save_and_dedupe_and_settle():
    store = _store()
    sel = {"sport": "nba", "match_label": "A vs B", "event_id": "e1",
           "market_type": "moneyline", "line": None, "outcome": "home",
           "odds_decimal": 2.0, "tier": "obvious", "edge": 0.07, "ev": 0.1,
           "stake_cap": 2.0, "thesis": "t", "invalidation": "i", "sources": ["a", "b"]}
    first = store.save_selection(sel)
    assert first
    assert store.save_selection(sel) is None  # duplicate open
    store.settle(first, "won")
    reopened = store.save_selection(sel)
    assert reopened and reopened != first  # terminal picks don't block re-entry
    assert store.save_selection(sel) is None  # but only one open at a time
    report = store.stats_for_day()
    assert report["counts"]["won"] >= 1


def test_subscription_and_record():
    store = _store()
    sub = store.ensure_subscription("123")
    assert sub["chat_id"] == "123"
    assert store.record_alltime() == []


def test_settle_1x2_and_total():
    home_win = {"market_type": "moneyline", "outcome": "home", "line": None}
    assert settle(home_win, {"home": 2, "away": 1}) == "won"
    assert settle(home_win, {"home": 0, "away": 1}) == "lost"
    assert settle(home_win, None) == "pending"
    over = {"market_type": "total", "outcome": "over", "line": "2.5"}
    assert settle(over, {"home": 2, "away": 1}) == "won"
    assert settle(over, {"home": 1, "away": 0}) == "lost"
    push = {"market_type": "total", "outcome": "over", "line": "3.0"}
    assert settle(push, {"home": 2, "away": 1}) == "void"
