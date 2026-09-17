"""Kalshi public trade API client (no auth for reads). Prices are 0-100 cents."""
from __future__ import annotations

from .base import LiveEvent, MarketPrice, OutcomePrice, Source
from .http import get_json

API = "https://api.elections.kalshi.com/trade-api/v2"

SERIES = {
    "nba": "KXNBA",
    "nfl": "KXNFL",
    "mlb": "KXMLB",
    "nhl": "KXNHL",
    "soccer-epl": "KXEPL",
    "soccer-ucl": "KXUCL",
    "soccer-laliga": "KXLALIGA",
    "soccer-bundesliga": "KXBUNDESLIGA",
    "soccer-seriea": "KXSERIEA",
    "soccer-ligue1": "KXLIGUE1",
    "tennis-atp": "KXATP",
}


class KalshiSource(Source):
    name = "kalshi"

    def fetch_live(self, sport: str) -> list[LiveEvent]:
        ticker = SERIES.get(sport)
        if not ticker:
            return []
        try:
            data = get_json(f"{API}/markets",
                            params={"series_ticker": ticker, "status": "open",
                                    "limit": 100})
        except Exception:
            return []
        events: list[LiveEvent] = []
        for m in (data.get("markets") or []):
            try:
                yes = float(m.get("yes_bid") or m.get("last_price") or 0)
                no = 100 - yes if yes else 0
                if yes <= 0 or yes >= 100:
                    continue
                volume = float(m.get("volume") or 0)
                events.append(LiveEvent(
                    event_id=f"kalshi-{m.get('ticker')}",
                    sport=sport,
                    match_label=m.get("title") or m.get("event_ticker", "?"),
                    is_live=True,
                    markets=[MarketPrice(
                        market_type="moneyline", line=None,
                        outcomes=[OutcomePrice("yes", 100 / yes, volume),
                                  OutcomePrice("no", 100 / no, volume)])],
                ))
            except Exception:
                continue
        return events
