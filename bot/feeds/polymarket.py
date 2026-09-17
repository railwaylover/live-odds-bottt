"""Polymarket Gamma API client (keyless, browser UA required)."""
from __future__ import annotations

from .base import LiveEvent, MarketPrice, OutcomePrice, Source
from .http import get_json

GAMMA = "https://gamma-api.polymarket.com"

# sport key -> keyword filter used against event titles/series
SPORT_KEYWORDS = {
    "soccer-epl": ["premier league", "epl"],
    "soccer-laliga": ["la liga", "laliga"],
    "soccer-bundesliga": ["bundesliga"],
    "soccer-seriea": ["serie a"],
    "soccer-ligue1": ["ligue 1"],
    "soccer-ucl": ["champions league"],
    "nba": ["nba"],
    "nfl": ["nfl"],
    "mlb": ["mlb"],
    "nhl": ["nhl"],
    "tennis-atp": ["atp", "tennis"],
}


class PolymarketSource(Source):
    name = "polymarket"

    def fetch_live(self, sport: str) -> list[LiveEvent]:
        # No keyword prefilter: sports liquidity moves across series/titles.
        # Matching to fixtures happens in monitor.py via team-token overlap.
        try:
            data = get_json(f"{GAMMA}/events",
                            params={"closed": "false", "limit": 150})
        except Exception:
            return []
        events: list[LiveEvent] = []
        for ev in data or []:
            title = ev.get("title") or ""
            markets: list[MarketPrice] = []
            for m in ev.get("markets") or []:
                try:
                    outcomes = m.get("outcomes")
                    prices = m.get("outcomePrices")
                    if isinstance(outcomes, str):
                        import json as _json
                        outcomes = _json.loads(outcomes)
                        prices = _json.loads(prices)
                    if not outcomes or not prices:
                        continue
                    volume = float(m.get("volume") or 0)
                    ops = [OutcomePrice(name=str(o),
                                        decimal_odds=(1 / float(p)) if float(p) > 0 else 0.0,
                                        volume=volume)
                           for o, p in zip(outcomes, prices) if float(p) > 0]
                    if len(ops) >= 2:
                        markets.append(MarketPrice(market_type="moneyline",
                                                   line=None, outcomes=ops))
                except Exception:
                    continue
            if markets:
                events.append(LiveEvent(
                    event_id=f"poly-{ev.get('id')}",
                    sport=sport,
                    match_label=ev.get("title", "?"),
                    is_live=True,
                    markets=markets,
                ))
        return events
