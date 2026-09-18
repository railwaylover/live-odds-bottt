import asyncio
import tempfile
from unittest.mock import AsyncMock, MagicMock

from bot import commands
from bot.notify import format_result, format_status
from bot.store import Store


def _ctx(store):
    update = MagicMock()
    update.effective_chat.id = 111
    update.message.reply_text = AsyncMock()
    ctx = MagicMock()
    ctx.application.bot_data = {"store": store}
    ctx.args = []
    return update, ctx


def _store(tmp=None):
    store = Store(path=tempfile.mktemp(suffix=".db"))
    return store


def test_gate_reads_store_from_application():
    """Regression: _gate must use ctx.application.bot_data (Message has no bot_data)."""
    import bot.config as config
    old = config.AUTHORIZED_CHAT_IDS
    config.AUTHORIZED_CHAT_IDS = ["111"]
    try:
        store = _store()
        update, ctx = _ctx(store)
        result = asyncio.run(commands._gate(update, ctx))
        assert result is store
    finally:
        config.AUTHORIZED_CHAT_IDS = old


def test_start_replies():
    import bot.config as config
    old = config.AUTHORIZED_CHAT_IDS
    config.AUTHORIZED_CHAT_IDS = ["111"]
    try:
        update, ctx = _ctx(_store())
        asyncio.run(commands.start(update, ctx))
        text = update.message.reply_text.await_args[0][0]
        assert "Live Odds Bot online" in text
    finally:
        config.AUTHORIZED_CHAT_IDS = old


def test_status_snapshot():
    import bot.config as config
    old = config.AUTHORIZED_CHAT_IDS
    config.AUTHORIZED_CHAT_IDS = ["111"]
    try:
        store = _store()
        sel_id = store.save_selection({
            "sport": "nba", "match_label": "A vs B", "event_id": "e9",
            "market_type": "moneyline", "line": None, "outcome": "home",
            "odds_decimal": 2.0, "tier": "obvious", "edge": 0.07, "ev": 0.1,
            "stake_cap": 2.0, "thesis": "t", "invalidation": "i",
            "sources": ["a", "b"]})
        store.settle(sel_id, "won")
        update, ctx = _ctx(store)
        asyncio.run(commands.status(update, ctx))
        text = update.message.reply_text.await_args[0][0]
        assert "Live status" in text and "1 won" in text
    finally:
        config.AUTHORIZED_CHAT_IDS = old


def test_format_result_messages():
    won = format_result({"status": "won", "tier": "obvious", "match_label": "A vs B",
                         "market_type": "moneyline", "outcome": "home", "odds_decimal": 2.0})
    lost = format_result({"status": "lost", "tier": "value", "match_label": "C vs D",
                          "market_type": "total", "outcome": "over", "odds_decimal": 1.9})
    assert "✅ Bet WON" in won and "A vs B" in won
    assert "❌ Bet LOST" in lost and "C vs D" in lost


def test_dispatch_result_pushes_to_subscribers():
    from bot import monitor
    store = _store()
    store.ensure_subscription("111")
    bot = MagicMock()
    bot.send_message = AsyncMock(return_value=True)
    sel = {"id": "x1", "tier": "obvious", "status": "won", "match_label": "A vs B",
           "market_type": "moneyline", "outcome": "home", "odds_decimal": 2.0}
    asyncio.run(monitor.dispatch_result(store, bot, sel))
    sent = bot.send_message.await_args
    assert sent is not None
    assert "✅ Bet WON" in sent.kwargs.get("text", sent.args[0] if sent.args else "")
    assert store.alert_exists("x1", "111")


def test_format_status_truncates_long_lists():
    picks = [{"tier": "value", "match_label": f"T{i} vs U{i}", "market_type": "moneyline",
              "outcome": "home", "odds_decimal": 2.0} for i in range(12)]
    text = format_status(picks, {"won": 3, "lost": 1, "void": 0, "pending": 0}, "2026-09-18")
    assert "Open picks: 12" in text and "more (see /opportunities)" in text
    assert "3 won" in text and "1 lost" in text
