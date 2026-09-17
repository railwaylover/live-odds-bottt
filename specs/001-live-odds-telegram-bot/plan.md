# Implementation Plan: Live Odds Telegram Bot

**Branch**: `001-live-odds-telegram-bot` | **Date**: 2026-09-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-live-odds-telegram-bot/spec.md`

## Summary

Telegram bot that monitors live matches across all sports via keyless feeds
(ESPN scoreboard odds, Polymarket, Kalshi), runs every candidate through a
local edge-analysis engine (de-vig → corroboration → movement check →
thesis), pushes tiered alerts (🟢 obvious / 🟡 value) to two authorized
private chats, and settles results behind `/stats` (Tehran day) and
`/record`. $0 cost, recommends-only, unpriceable markets reported as gaps.

## Technical Context

**Language/Version**: Python 3.10+ (verified 3.13.5 in build env)

**Primary Dependencies**: `python-telegram-bot` v21 (verified installed),
stdlib `sqlite3`, `urllib`/`http.client` with browser UA (no new packages
required)

**Storage**: SQLite (WAL mode) at `data/bot.db` + daily JSON snapshots

**Testing**: `pytest` (stdlib `unittest` fallback if pytest unavailable)

**Target Platform**: Linux server / free Python host (long-polling, no
inbound networking needed)

**Project Type**: Long-running service (Telegram bot + monitor loop)

**Performance Goals**: Staged edge → delivered alert within 3 minutes;
monitor cycle per sport within its cadence budget (live 60–120s, pre-match
15–60min)

**Constraints**: $0 spend; secrets via env only; Telegram + source rate
limits respected with queue/backoff; Asia/Tehran day boundaries

**Scale/Scope**: 2 authorized chats; all ESPN-covered sports; market catalog
per sport vs 1xBet taxonomy; single-process service

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- I. Profitability First → two-tier edge thresholds + stake caps; PASS
- II. Analytical Excellence → full pipeline per selection, thesis +
  invalidation mandatory; PASS
- III. Relentless Solution-Finding → graceful degradation, never offline;
  PASS
- IV. Always-On → auto-restart, WAL persistence, heartbeat; PASS
- V. Zero-Cost → keyless feeds, SQLite, free host, no paid deps; PASS
- VI. Communication Excellence → fixed alert/command formats in
  contracts/commands.md; PASS
- VII. Skill Diligence → betting/markets/the-odds-api/football-data skills
  audited and mapped in research.md; PASS
- VIII. Complete Market Coverage → per-sport catalog + gap reporting
  (FR-009, US4); PASS
- Bookmaker-neutral accuracy → ≥2-source corroboration, outlier discard,
  no-guess settlement; PASS

Post-design re-check: no new violations introduced. No complexity-tracking
entries needed.

## Project Structure

### Documentation (this feature)

```text
specs/001-live-odds-telegram-bot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── commands.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
bot/
├── main.py              # entrypoint: PTB app + JobQueue wiring
├── config.py            # env-only settings, Tehran tz, thresholds
├── store.py             # SQLite persistence (selections/alerts/subs/gaps)
├── monitor.py           # tiered polling loop + quota budgeting
├── feeds/
│   ├── base.py          # source interface + normalized event model
│   ├── espn.py          # ESPN scoreboard odds client
│   ├── polymarket.py    # Gamma API client (browser UA)
│   └── kalshi.py        # Kalshi public API client
├── analysis/
│   ├── odds.py          # conversion, de-vig, edge/EV, Kelly-lite
│   ├── movement.py      # line-movement classification
│   ├── pipeline.py      # full candidate evaluation + tiering
│   └── markets.py       # per-sport catalog vs 1xBet taxonomy + gaps
├── notify.py            # alert formatting + queued sends + quiet hours
├── settle.py            # feed-driven settlement
├── commands.py          # all bot command handlers
└── catalog/
    └── markets.yaml     # per-sport market-type catalog + gap flags

tests/
├── test_odds.py
├── test_pipeline.py
├── test_store.py
├── test_notify.py
└── test_settle.py

scripts/
├── stage_fixture.py     # stage a known edge for alert tests
└── seed_results.py      # seed settled picks for /stats tests

requirements.txt  Procfile  render.yaml  .env.example  .gitignore
```

**Structure Decision**: Single Python service package (`bot/`) with feed
adapters behind one interface, local analysis engine, SQLite store; flat
`tests/` + `scripts/` harnesses per quickstart.md.

## Complexity Tracking

> No constitution violations to justify. Table intentionally empty.
