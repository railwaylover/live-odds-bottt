"""Seed settled picks for /stats testing. Usage: seed_results.py --date YYYY-MM-DD"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import config
from bot.store import Store


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    args = ap.parse_args()
    store = Store()
    outcomes = ["won", "lost", "void", "won"]
    for i, status in enumerate(outcomes):
        sel_id = store.save_selection({
            "sport": "nba", "match_label": f"Seed {i} vs Test", "event_id": f"seed-{i}",
            "market_type": "moneyline", "line": None, "outcome": "home",
            "odds_decimal": 2.0, "tier": "obvious" if i % 2 == 0 else "value",
            "edge": 0.07, "ev": 0.1, "stake_cap": 1.0, "thesis": "seed",
            "invalidation": "seed", "sources": ["espn", "polymarket"]})
        if sel_id:
            store.settle(sel_id, status)
    print(f"seeded 4 picks; check /stats for {args.date or 'today'}")


if __name__ == "__main__":
    main()
