# Research: Live Odds Telegram Bot

**Date**: 2026-09-17 | **Feature**: `001-live-odds-telegram-bot`

All unknowns resolved by live probes run from the build environment on
2026-09-17. No NEEDS CLARIFICATION remains.

## Decision 1: Telegram framework → python-telegram-bot v21 (asyncio)

- **Decision**: Build on `python-telegram-bot` (PTB) v21, already installed
  (verified `telegram.__version__ == 21.10`), Python 3.13. Use `JobQueue`
  for the monitor loop and command handlers for all bot commands.
- **Rationale**: Installed and importable with zero new cost; asyncio-native
  fits polling + periodic monitor + queued sends; mature rate-limit handling.
- **Alternatives considered**: aiogram 3 (not installed; no advantage worth
  a new dependency); raw Bot API via httpx (reinvents queuing/backoff).

## Decision 2: Odds feeds → keyless hybrid (ESPN + Polymarket + Kalshi)

- **Decision**: Primary feeds, all keyless and probed live (HTTP 200):
  1. ESPN scoreboard API (`site.api.espn.com/.../scoreboard`) — carries
     sportsbook odds blocks per event (verified `odds` present on EPL event).
  2. Polymarket Gamma API (`gamma-api.polymarket.com`) — Yes/No markets
     with `outcomes`/`outcomePrices`; requires a browser `User-Agent`
     header (bare urllib got 403, curl with UA got 200).
  3. Kalshi trade API (`api.elections.kalshi.com`) — public reads, no auth;
     prices on 0–100 integer scale.
- **Rationale**: Satisfies the $0 and no-daily-keys constraints; two/three
  independent price sources enable the mandatory corroboration rule.
- **Alternatives considered**: The Odds API (rejected as primary — 500
  req/month quota burns out under 24/7 all-sports polling; kept as optional
  booster only); 1xBet endpoints (rejected — no public lawful free API,
  scraping risks bans and violates the reliability principle).

## Decision 3: Analysis math → local engine (port of `betting` skill logic)

- **Decision**: Implement de-vig, fair probability, edge/EV, Kelly-lite
  stake caps, and line-movement classification as pure local functions in
  `bot/analysis/` (same formulas as the audited `betting` skill: American ↔
  decimal ↔ probability conversion, overround removal, cross-source edge).
- **Rationale**: Zero network, zero cost, fully testable; no dependency on
  the `sports-skills` package being installable in deployment.
- **Alternatives considered**: `pip install sports-skills` at runtime
  (rejected — external install dependency on a free host hurts reliability).

## Decision 4: Enrichment → ESPN stats + ClubElo-style baselines, best-effort

- **Decision**: Thesis enrichment pulls what free endpoints offer per match
  (standings, recent form, H2H where available); missing enrichment degrades
  the thesis text but never blocks a well-corroborated price edge.
- **Rationale**: Price edge is the profit signal; enrichment is the required
  written justification. Decoupling keeps alerts flowing when stats lag.
- **Alternatives considered**: Blocking on full enrichment (rejected —
  threatens uptime and alert latency).

## Decision 5: Storage → SQLite (WAL mode) + JSON snapshot export

- **Decision**: SQLite file (`data/bot.db`, WAL) for selections, alerts,
  subscriptions, gaps; daily JSON snapshot for the `/stats` audit trail.
- **Rationale**: Zero-cost, zero-service, survives restarts on free hosts
  with persistent disks; trivial backup by copying one file.
- **Alternatives considered**: Postgres/Redis (rejected — needs a paid or
  ephemeral free service, violates simplicity and $0 robustness).

## Decision 6: Runtime/scheduling → long-polling + JobQueue, systemd/supervisor config + free-host deploy

- **Decision**: PTB long-polling (no public webhook URL needed on free
  tiers); monitor cadence tiered (live/in-play fast, pre-match slow);
  ship `Procfile`, `render.yaml`, and keep-alive heartbeat; secrets strictly
  via environment variables.
- **Rationale**: Works on every free Python host without inbound networking;
  polling intervals are the quota-budget enforcement point.
- **Alternatives considered**: Webhooks (rejected — free tiers often lack
  stable inbound HTTPS); paid always-on VPS (rejected — $0 ceiling).

## Decision 7: Settlement → feed-driven where possible, explicit otherwise

- **Decision**: Settle from final scores on the same free scoreboard feeds;
  markets that cannot be auto-settled stay `pending` and are excluded from
  win/loss tallies until resolved, never guessed.
- **Rationale**: Protects the accuracy rule; a pending pick must not corrupt
  the track record.
