import os
import tempfile

from bot.notify import format_alert, format_stats, in_quiet_hours


def _sel():
    return {"sport": "nba", "match_label": "A vs B", "market_type": "moneyline",
            "line": None, "outcome": "home", "odds_decimal": 2.1, "tier": "obvious",
            "edge": 0.08, "ev": 0.17, "stake_cap": 2.0,
            "thesis": "fair vs market", "invalidation": "drift"}


def test_format_alert_has_required_fields():
    text = format_alert(_sel())
    for needle in ["A vs B", "2.1", "Thesis:", "Invalid if:", "🟢"]:
        assert needle in text


def test_format_stats_empty_and_full():
    assert "No selections" in format_stats({"day": "2026-01-01", "picks": [],
                                            "counts": {}})
    row = dict(_sel(), status="won")
    text = format_stats({"day": "2026-01-01", "picks": [row],
                         "counts": {"won": 1, "lost": 0, "void": 0, "pending": 0}})
    assert "✅" in text and "Tally" in text


def test_quiet_hours_overnight():
    from datetime import datetime
    from bot import config
    sub = {"quiet_start": "22:00", "quiet_end": "07:00"}
    night = datetime(2026, 1, 1, 23, 0, tzinfo=config.TEHRAN_TZ)
    day = datetime(2026, 1, 1, 12, 0, tzinfo=config.TEHRAN_TZ)
    assert in_quiet_hours(sub, night) is True
    assert in_quiet_hours(sub, day) is False
