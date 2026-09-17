"""Tiered polling loop with quota budgeting and graceful degradation."""
from __future__ import annotations

import asyncio
import logging
import time

from . import config
from .analysis import markets as catalog
from .analysis import pipeline
from .feeds.base import LiveEvent, Source
from .feeds.espn import EspnSource
from .feeds.kalshi import KalshiSource
from .feeds.polymarket import PolymarketSource
from .notify import format_alert, in_quiet_hours, send_with_backoff
from .settle import settle
from .store import Store

log = logging.getLogger("live-odds-bot")

SOURCES: list[Source] = [EspnSource(), PolymarketSource(), KalshiSource()]

# Per-source call budget per cycle; exhausted meters degrade instead of dying
CALL_BUDGET = {"espn": 40, "polymarket": 20, "kalshi": 20}


def _key(ev: LiveEvent) -> str:
    return f"{ev.sport}|{ev.match_label}".lower()


STOPWORDS = {"vs", "v", "the", "fc", "cf", "sc", "ac", "united", "city",
             "real", "club", "de", "la", "le", "les", "at", "of", "and"}

# Cities with multiple major teams: a bare city token must not join fixtures.
CITY_TOKENS = {"toronto", "london", "madrid", "milan", "manchester", "paris",
               "moscow", "istanbul", "los", "angeles", "new", "york", "mexico",
               "buenos", "aires", "rio", "sao", "paulo", "rome", "berlin"}


def team_tokens(label: str) -> set[str]:
    toks = set()
    for part in label.lower().replace("vs.", " ").replace("vs", " ").split():
        word = "".join(c for c in part if c.isalnum())
        if len(word) > 2 and word not in STOPWORDS:
            toks.add(word)
    return toks


def same_match(a: LiveEvent, b: LiveEvent) -> bool:
    """Fuzzy fixture join across heterogeneous source labels."""
    if _key(a) == _key(b):
        return True
    ta, tb = team_tokens(a.match_label), team_tokens(b.match_label)
    if not ta or not tb:
        return False
    overlap = ta & tb
    if len(overlap) >= 2:
        return True
    if len(overlap) == 1:
        tok = next(iter(overlap))
        # single shared token only counts if distinctive, long, and not a
        # multi-team city (e.g. Toronto Maple Leafs vs Toronto Raptors)
        return len(tok) >= 8 and tok not in CITY_TOKENS
    la, lb = a.match_label.lower(), b.match_label.lower()
    return (len(la) > 8 and la in lb) or (len(lb) > 8 and lb in la)


FETCH_TIMEOUT = 12
MAX_CONCURRENT_FETCHES = 8


async def _fetch_one(sem: asyncio.Semaphore, src: Source, sport: str):
    async with sem:
        try:
            evs = await asyncio.wait_for(
                asyncio.to_thread(src.fetch_live, sport), timeout=FETCH_TIMEOUT)
            return src.name, sport, evs or []
        except Exception as exc:
            log.warning("feed %s failed for %s: %s", src.name, sport, exc)
            return src.name, sport, []


async def run_cycle(store: Store, bot=None) -> dict:
    """One monitor pass over all catalog sports. Returns cycle stats."""
    stats = {"evaluated": 0, "alerted": 0, "discarded": 0, "degraded": []}
    remaining = dict(CALL_BUDGET)
    sem = asyncio.Semaphore(MAX_CONCURRENT_FETCHES)
    jobs = []
    for sport in catalog.all_sports():
        for src in SOURCES:
            if remaining.get(src.name, 0) <= 0:
                if src.name not in stats["degraded"]:
                    stats["degraded"].append(src.name)
                continue
            remaining[src.name] -= 1
            jobs.append(_fetch_one(sem, src, sport))
    per_sport: dict[str, dict[str, list[LiveEvent]]] = {}
    for name, sport, evs in await asyncio.gather(*jobs):
        per_sport.setdefault(sport, {})[name] = evs
    for sport in catalog.all_sports():
        per_source = per_sport.get(sport, {})
        # Build one candidate pool from ALL sources, joined by fuzzy
        # fixture matching, so any single-source outage degrades gracefully.
        pool: list[LiveEvent] = []
        for src in SOURCES:
            for ev in per_source.get(src.name, []):
                if not ev.markets:
                    continue
                ev.source_name = src.name
                pool.append(ev)
        groups: list[list[LiveEvent]] = []
        for ev in pool:
            placed = False
            for g in groups:
                if any(same_match(ev, member) for member in g):
                    if not any(m.source_name == ev.source_name for m in g):
                        g.append(ev)
                    placed = True
                    break
            if not placed:
                groups.append([ev])
        for members in groups:
            if len(members) < 2:
                ev = members[0]
                store.upsert_gap(ev.sport, ev.markets[0].market_type,
                                 "single-source-only")
                stats["discarded"] += 1
                continue
            # Primary = ESPN event when present, else first available.
            by_source = {e.source_name: e for e in members}
            ev = by_source.get("espn") or members[0]
            corroborating = [e for e in members if e is not ev]
            if not catalog.is_monitored(ev.sport, ev.markets[0].market_type):
                store.upsert_gap(ev.sport, ev.markets[0].market_type,
                                 "not-in-catalog")
                continue
            stats["evaluated"] += 1
            sel = pipeline.evaluate(ev, corroborating)
            if not sel:
                stats["discarded"] += 1
                continue
            sel_id = store.save_selection(sel)
            if not sel_id:
                continue  # duplicate open selection
            sel["id"] = sel_id
            stats["alerted"] += 1
            if bot is not None:
                await dispatch(store, bot, sel)
    await settle_open(store)
    return stats


async def settle_open(store: Store) -> int:
    """Settle open picks from one batched ESPN finals pass. Returns count."""
    espn = next((s for s in SOURCES if s.name == "espn"), None)
    if espn is None or not hasattr(espn, "fetch_finals"):
        return 0
    try:
        finals = await asyncio.to_thread(espn.fetch_finals)
    except Exception as exc:
        log.warning("finals fetch failed: %s", exc)
        return 0
    settled = 0
    for sel in store.get_open():
        final = finals.get(str(sel["event_id"]))
        if final is None:
            continue
        outcome = settle(sel, final)
        if outcome in ("won", "lost", "void"):
            store.settle(sel["id"], outcome)
            settled += 1
    return settled


async def dispatch(store: Store, bot, sel: dict) -> None:
    text = format_alert(sel)
    for sub in store.subscribers_for_tier(sel["tier"]):
        chat_id = sub["chat_id"]
        if store.alert_exists(sel["id"], chat_id):
            continue
        if in_quiet_hours(sub):
            store.record_alert(sel["id"], chat_id, state="queued")
            continue
        ok = await send_with_backoff(bot, chat_id, text)
        store.record_alert(sel["id"], chat_id, state="sent" if ok else "failed")


async def monitor_forever(store: Store, bot) -> None:
    log.info("monitor loop started")
    while True:
        started = time.monotonic()
        try:
            stats = await run_cycle(store, bot)
            log.info("cycle done: %s", stats)
        except Exception as exc:
            log.exception("cycle failed: %s", exc)
        elapsed = time.monotonic() - started
        await asyncio.sleep(max(config.LIVE_CADENCE - elapsed, 10))
