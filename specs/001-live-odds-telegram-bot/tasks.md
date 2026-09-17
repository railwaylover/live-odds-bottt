# Tasks: Live Odds Telegram Bot

**Feature**: `001-live-odds-telegram-bot` | **Plan**: [plan.md](plan.md)

## Dependencies (story completion order)

US1 (obvious alerts) → US2 (value alerts) → US3 (stats/record) → US4
(market catalog + gaps) → US5 (commands/subscriptions). Setup (Phase 1)
and Foundational (Phase 2) block all stories. MVP = Phases 1–3.

## Phase 1: Setup

- [x] T001 Create project scaffold per plan structure in `bot/`, `tests/`, `scripts/`
- [x] T002 [P] Create `requirements.txt` (python-telegram-bot>=21) and `.env.example` (TELEGRAM_BOT_TOKEN, AUTHORIZED_CHAT_IDS) in repo root
- [x] T003 [P] Create `.gitignore` (Python set: `__pycache__/`, `*.pyc`, `.venv/`, `data/*.db`, `.env`) in repo root
- [x] T004 [P] Create `Procfile`, `render.yaml` (free-tier worker, `python -m bot.main`) in repo root
- [x] T005 Implement `bot/config.py` (env-only settings, Asia/Tehran tz, tier thresholds, cadences)

## Phase 2: Foundational

- [x] T006 Implement `bot/store.py` (SQLite WAL: selections, alerts, subscriptions, gaps per data-model.md)
- [x] T007 Implement `bot/feeds/base.py` (source interface + normalized event model per contracts/commands.md)
- [x] T008 [P] Implement `bot/feeds/espn.py` (scoreboard odds client with rate-limit respect)
- [x] T009 [P] Implement `bot/feeds/polymarket.py` (Gamma client with browser UA + volume filter)
- [x] T010 [P] Implement `bot/feeds/kalshi.py` (public API client, 0–100 scale normalization)
- [x] T011 Implement `bot/analysis/odds.py` (conversion, de-vig, edge/EV, Kelly-lite caps)
- [x] T012 Implement `bot/analysis/movement.py` (line-movement classification)
- [x] T013 Implement `bot/monitor.py` (tiered polling loop + quota budgeting + dedupe identity)
- [x] T014 Implement `bot/main.py` (PTB app, JobQueue wiring, graceful shutdown, heartbeat log)

## Phase 3: US1 — Obvious-edge live alerts (P1)

**Goal**: Staged mispriced market yields a formatted 🟢 alert in both chats.
**Independent test**: `scripts/stage_fixture.py --tier obvious` → alerts within 3 min; re-run → no duplicate.

- [x] T015 [US1] Implement `bot/analysis/pipeline.py` obvious-tier evaluation (corroboration ≥2 sources, outlier discard) in `bot/analysis/pipeline.py`
- [x] T016 [US1] Implement `bot/notify.py` alert formatting + queued delivery per contracts/commands.md
- [x] T017 [US1] Create `scripts/stage_fixture.py` (stage known edges per tier) in `scripts/stage_fixture.py`
- [x] T018 [US1] Create `tests/test_pipeline.py` (edge math, tiering, outlier discard) in `tests/test_pipeline.py`
- [x] T019 [US1] Create `tests/test_notify.py` (format fields incl. thesis/invalidation, no-duplicate) in `tests/test_notify.py`

## Phase 4: US2 — Value-tier alerts (P1)

**Goal**: Moderate-edge markets yield distinct 🟡 alerts with edge/EV/cap.
**Independent test**: stage `--tier value` → labeled value alert; thin-volume market → withheld.

- [x] T020 [US2] Extend `bot/analysis/pipeline.py` with value-tier floor, volume guard, stake caps
- [x] T021 [US2] Extend `tests/test_pipeline.py` with value-tier and thin-volume cases

## Phase 5: US3 — Daily statistics and record (P1)

**Goal**: `/stats` lists every Tehran-day pick with correct outcome markers + tally; `/record` all-time.
**Independent test**: `scripts/seed_results.py` → `/stats` and `/record` verified.

- [x] T022 [US3] Implement `bot/settle.py` (feed-driven settlement; unsettlable → pending, never guessed)
- [x] T023 [US3] Implement `/stats` + `/record` handlers in `bot/commands.py`
- [x] T024 [US3] Create `scripts/seed_results.py` (seed settled picks for stats tests) in `scripts/seed_results.py`
- [x] T025 [US3] Create `tests/test_settle.py` + `tests/test_store.py` (settlement transitions, Tehran day grouping) in `tests/`

## Phase 6: US4 — Market catalog + gap reporting (P2)

**Goal**: Per-sport catalog monitored; unpriceable markets appear as gaps, never alerts.
**Independent test**: enable a market type → flows to alert; unpriceable one → gap report only.

- [x] T026 [US4] Implement `bot/analysis/markets.py` (catalog checks + gap registry) in `bot/analysis/markets.py`
- [x] T027 [US4] Create `bot/catalog/markets.yaml` (per-sport market types vs 1xBet taxonomy + gap flags)
- [x] T028 [US4] Implement `/coverage` handler in `bot/commands.py`

## Phase 7: US5 — Commands and subscriptions (P2)

**Goal**: All commands work; unsubscribed/quiet-hour behavior correct.
**Independent test**: invoke each command against seeded store; verify states.

- [x] T029 [US5] Implement `/start`, `/help`, `/opportunities` handlers in `bot/commands.py`
- [x] T030 [US5] Implement `/subscribe`, `/unsubscribe`, `/settings` (tiers, quiet hours) + auth-gate in `bot/commands.py`
- [x] T031 [US5] Extend `bot/notify.py` with quiet-hour queueing + Telegram backoff

## Phase 8: Polish & cross-cutting

- [x] T032 Restart-recovery verification (WAL persistence, resume with no manual steps) in `bot/main.py`
- [x] T033 Secrets audit (no token/key in code or logs; env-only) across `bot/`
- [ ] T034 7-day dry-run checklist + heartbeat doc in `specs/001-live-odds-telegram-bot/quickstart.md`
- [x] T035 Run full suite `python -m pytest tests/ -q`; all green

## Parallel opportunities

- T002–T004 (scaffold files) run parallel after T001.
- T008–T010 (feed clients) run parallel after T007.
- T018–T019, T021, T025 test files run parallel with their implementation tasks.
