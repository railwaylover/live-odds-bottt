from bot.settle import settle_total, settle_1x2


def test_exotic_never_guessed():
    sel = {"market_type": "cards-total", "outcome": "over", "line": "3.5"}
    from bot.settle import settle
    assert settle(sel, {"home": 2, "away": 1}) == "pending"


def test_draw_result():
    sel = {"market_type": "1x2", "outcome": "draw", "line": None}
    assert settle_1x2(sel, {"home": 1, "away": 1}) == "won"
    assert settle_1x2(sel, {"home": 2, "away": 1}) == "lost"
