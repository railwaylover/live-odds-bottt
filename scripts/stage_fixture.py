"""Stage a known edge for alert testing. Usage: stage_fixture.py --tier obvious|value"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import config
from bot.analysis import pipeline
from bot.feeds.base import LiveEvent, MarketPrice, OutcomePrice
from bot.store import Store


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", choices=["obvious", "value"], default="obvious")
    args = ap.parse_args()
    fair_home = 0.72 if args.tier == "obvious" else 0.58
    market_home = 2.0 if args.tier == "obvious" else 1.95
    ev = LiveEvent("stage-1", "nba", "Staged A vs Staged B", True,
                   [MarketPrice("moneyline", None,
                                [OutcomePrice("home", 1 / fair_home),
                                 OutcomePrice("away", 1 / (1 - fair_home))])])
    ev.source_name = "espn"
    cor = LiveEvent("stage-x", "nba", "Staged A vs Staged B", True,
                    [MarketPrice("moneyline", None,
                                 [OutcomePrice("home", market_home, 1000.0),
                                  OutcomePrice("away", 3.0, 1000.0)])])
    cor.source_name = "polymarket"
    sel = pipeline.evaluate(ev, [cor], enrichment="staged fixture for testing")
    store = Store()
    sel_id = store.save_selection(sel) if sel else None
    print(f"tier={sel['tier'] if sel else None} id={sel_id}")
    assert sel and sel["tier"] == args.tier, "staged edge did not qualify as expected"


if __name__ == "__main__":
    main()
