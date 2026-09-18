"""Alert formatting + delivery with quiet hours, tiers, and backoff."""
from __future__ import annotations

import asyncio
from datetime import datetime

from . import config

TIER_EMOJI = {"obvious": "🟢", "value": "🟡"}
OUTCOME_EMOJI = {"won": "✅", "lost": "❌", "void": "➖", "pending": "⏳", "open": "🔵"}


def format_alert(sel: dict) -> str:
    badge = TIER_EMOJI.get(sel["tier"], "⚪")
    tier_name = "OBVIOUS EDGE" if sel["tier"] == "obvious" else "VALUE PICK"
    line = f" — Line {sel['line']}" if sel.get("line") else ""
    return (
        f"{badge} {tier_name} — {sel['sport']}\n"
        f"{sel['match_label']} — {sel['market_type']}{line}: "
        f"{sel['outcome']} @ {sel['odds_decimal']}\n"
        f"Edge {sel['edge']:.1%} · EV {sel['ev']:+.2f}u · Cap {sel['stake_cap']}u\n"
        f"Thesis: {sel['thesis']}\n"
        f"Invalid if: {sel['invalidation']}"
    )


def in_quiet_hours(sub: dict, now: datetime | None = None) -> bool:
    qs, qe = sub.get("quiet_start"), sub.get("quiet_end")
    if not qs or not qe:
        return False
    now = now or datetime.now(config.TEHRAN_TZ)
    cur = now.strftime("%H:%M")
    if qs <= qe:
        return qs <= cur < qe
    return cur >= qs or cur < qe  # overnight window


async def send_with_backoff(bot, chat_id: str, text: str, retries: int = 3) -> bool:
    delay = 2
    for attempt in range(retries):
        try:
            await bot.send_message(chat_id=chat_id, text=text)
            return True
        except Exception:
            if attempt == retries - 1:
                return False
            await asyncio.sleep(delay)
            delay *= 2
    return False


def format_stats(report: dict) -> str:
    lines = [f"📊 Selections for {report['day']} (Asia/Tehran)"]
    if not report["picks"]:
        return lines[0] + "\nNo selections today."
    for sel in report["picks"]:
        emo = OUTCOME_EMOJI.get(sel["status"], "❔")
        badge = TIER_EMOJI.get(sel["tier"], "⚪")
        lines.append(
            f"{emo} {badge} {sel['match_label']} — {sel['market_type']}: "
            f"{sel['outcome']} @ {sel['odds_decimal']} ({sel['status']})")
    c = report["counts"]
    lines.append(
        f"\nTally: ✅ {c.get('won', 0)} · ❌ {c.get('lost', 0)} · "
        f"➖ {c.get('void', 0)} · ⏳ {c.get('pending', 0) + c.get('open', 0)}")
    return "\n".join(lines)


def format_record(rows: list[dict]) -> str:
    if not rows:
        return "📈 No settled selections yet."
    lines = ["📈 All-time record (settled only)"]
    for r in rows:
        lines.append(f"{r['tier']}: {r['status']} × {r['count']}")
    return "\n".join(lines)


def format_status(open_picks: list[dict], day_counts: dict, day: str) -> str:
    """Live snapshot: open picks right now + today's settled tally."""
    lines = [f"📡 Live status — {day} (Asia/Tehran)"]
    lines.append(f"🔵 Open picks: {len(open_picks)}")
    for sel in open_picks[:10]:
        badge = TIER_EMOJI.get(sel["tier"], "⚪")
        lines.append(f"  {badge} {sel['match_label']} — {sel['market_type']}: "
                     f"{sel['outcome']} @ {sel['odds_decimal']}")
    if len(open_picks) > 10:
        lines.append(f"  …and {len(open_picks) - 10} more (see /opportunities)")
    lines.append(
        f"\nToday settled: ✅ {day_counts.get('won', 0)} won · "
        f"❌ {day_counts.get('lost', 0)} lost · "
        f"➖ {day_counts.get('void', 0)} void · "
        f"⏳ {day_counts.get('pending', 0)} pending")
    return "\n".join(lines)


def format_result(sel: dict) -> str:
    """Push notification for a settled pick: live won/lost update."""
    emo = {"won": "✅ Bet WON", "lost": "❌ Bet LOST", "void": "➖ Bet VOID"}.get(
        sel["status"], "❔ Bet UPDATE")
    badge = TIER_EMOJI.get(sel["tier"], "⚪")
    return (
        f"{emo} {badge}\n"
        f"{sel['match_label']} — {sel['market_type']}: "
        f"{sel['outcome']} @ {sel['odds_decimal']}"
    )
