"""Feed-driven settlement. Unsettlable markets stay pending, never guessed."""
from __future__ import annotations

from .feeds.base import LiveEvent


def settle_1x2(selection: dict, final: dict | None) -> str:
    """Settle moneyline/1x2 given {'home': goals, 'away': goals} and outcome side."""
    if not final or "home" not in final or "away" not in final:
        return "pending"
    home, away = final["home"], final["away"]
    outcome = (selection.get("outcome") or "").lower()
    if home == away:
        winner = "draw"
    else:
        winner = "home" if home > away else "away"
    if outcome in ("yes", "no"):
        return "pending"  # prediction-market semantics need market-specific logic
    return "won" if outcome == winner else "lost"


def settle_total(selection: dict, final: dict | None) -> str:
    if not final or selection.get("line") is None:
        return "pending"
    try:
        total = final["home"] + final["away"]
        line = float(selection["line"])
    except (KeyError, TypeError, ValueError):
        return "pending"
    outcome = (selection.get("outcome") or "").lower()
    if total == line:
        return "void"
    is_over = total > line
    if outcome.startswith("over") or outcome == "yes":
        return "won" if is_over else "lost"
    if outcome.startswith("under") or outcome == "no":
        return "won" if not is_over else "lost"
    return "pending"


def settle(selection: dict, final: dict | None) -> str:
    mt = (selection.get("market_type") or "").lower()
    if mt in ("moneyline", "1x2"):
        return settle_1x2(selection, final)
    if mt.startswith("total"):
        return settle_total(selection, final)
    return "pending"  # exotic markets: explicit logic per type, never guessed
