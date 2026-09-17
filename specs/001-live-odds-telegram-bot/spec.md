# Feature Specification: Live Odds Telegram Bot

**Feature Branch**: `001-live-odds-telegram-bot`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: "Build a Telegram bot for identifying live betting odds
worth taking (obvious likely-winners with mispriced odds, plus riskier good-value
picks). Stay online 24/7 monitoring all sports/matches with a real analysis system
behind every selection. Push opportunities automatically plus bot commands including
daily statistics listing every selection with won/lost outcome. Zero cost. Private
alerts to two recipients (Asia/Tehran timezone). Full per-sport market-type coverage
(1xBet taxonomy reference); unpriceable markets reported as gaps, never alerted.
Bot recommends only, never places bets."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Obvious-edge live alerts (Priority: P1)

The user receives an automatic private Telegram message whenever the bot detects a
live market whose odds are clearly mispriced in the user's favor (high-confidence,
likely-win selection). Each alert contains the match, market, odds, tier badge,
written analysis thesis, and invalidation condition.

**Why this priority**: This is the core profit engine and the primary reason the
bot exists. Without it there is no product.

**Independent Test**: Can be fully tested by feeding a staged live fixture with a
known mispriced market and observing a correctly formatted alert delivered to both
recipient chats, and delivers the bot's main value on its own.

**Acceptance Scenarios**:

1. **Given** a live match with a market whose de-vigged edge exceeds the obvious
   tier threshold and passes corroboration, **When** the monitor cycle evaluates
   it, **Then** both recipients receive an alert within the configured latency
   budget containing match, market, odds, thesis, and invalidation.
2. **Given** a market whose edge is high on one feed but contradicted by the
   second source, **When** evaluated, **Then** no alert is sent and the event is
   logged as discarded.

---

### User Story 2 - Value-tier alerts for riskier picks (Priority: P1)

The user receives automatic alerts for riskier selections whose price still offers
positive expected value. These are visually distinct from obvious-edge alerts and
carry edge, EV estimate, and a capped stake suggestion.

**Why this priority**: The user explicitly wants both tiers; value picks are the
second half of the profit strategy.

**Independent Test**: Can be fully tested by staging a market with moderate edge
below the obvious threshold but above the value floor, and delivers distinct
value-tier alerts independently of US1.

**Acceptance Scenarios**:

1. **Given** a live market with edge between the value floor and the obvious
   threshold, corroborated by a second source, **When** evaluated, **Then** a
   value-tier alert is sent with edge, EV, and stake cap clearly labeled.
2. **Given** a market with positive edge on very thin market volume, **When**
   evaluated, **Then** it is withheld or flagged per the low-volume policy.

---

### User Story 3 - Daily statistics and track record (Priority: P1)

The user sends `/stats` and receives the day's full selection list (Asia/Tehran
day boundary), each row clearly marked won/lost/void/pending, plus a summary
tally. `/record` shows the all-time tally.

**Why this priority**: Transparency of results is how the user judges
profitability; it is a non-negotiable trust feature.

**Independent Test**: Can be fully tested by seeding settled selections for a day
and invoking `/stats`, delivering a complete accurate table without any live
monitoring running.

**Acceptance Scenarios**:

1. **Given** settled selections exist for the current Tehran day, **When** the
   user sends `/stats`, **Then** every selection is listed with correct outcome
   markers and a correct summary tally.
2. **Given** a day with no selections, **When** the user sends `/stats`, **Then**
   the bot replies with a clean empty-state message, not an error.

---

### User Story 4 - Full market-type coverage with gap reporting (Priority: P2)

The bot monitors each covered sport across its full market-type catalog
(moneyline, handicaps, totals, halves/periods, cards, corners, team scoring
segments, etc.) organized against the 1xBet reference taxonomy. Markets it
cannot accurately price never produce alerts and appear as declared coverage
gaps in statistics.

**Why this priority**: Coverage breadth multiplies opportunity surface, but it
depends on the US1/US2 pipeline existing first.

**Independent Test**: Can be fully tested by enabling an additional market type
for one sport and verifying it flows through analysis to alerts, while a
deliberately unpriceable market appears only in the gap report.

**Acceptance Scenarios**:

1. **Given** a newly enabled market type with reliable feeds, **When** a live
   edge appears in it, **Then** it produces tiered alerts like any other market.
2. **Given** a market type with no reliable free data, **When** the coverage
   report is viewed, **Then** it is listed as an uncovered gap and no alerts
   originate from it.

---

### User Story 5 - Bot commands and subscription control (Priority: P2)

The user interacts via commands: `/start`, `/help`, `/opportunities` (current
open picks), `/subscribe` / `/unsubscribe` (per-chat alert control),
`/settings` (tier preferences, quiet hours), alongside `/stats` and `/record`.

**Why this priority**: Control and introspection; depends on the alert pipeline
but is independently usable once picks exist.

**Independent Test**: Can be fully tested by invoking each command against a
seeded store and verifying correct responses and subscription state changes.

**Acceptance Scenarios**:

1. **Given** an unsubscribed chat, **When** no qualifying edge occurs, **Then**
   it receives no push alerts but can still use pull commands.
2. **Given** quiet hours are configured, **When** an edge occurs inside them,
   **Then** the alert is queued and delivered after quiet hours end.

---

### Edge Cases

- Feed outage on one source: analysis continues on remaining sources with a
  stricter corroboration stance; prolonged outage triggers an admin notice.
- Quota/budget exhaustion (metered feeds): bot degrades to keyless feeds
  rather than going offline, and states the degradation in `/stats`.
- Match ends or market suspends mid-analysis: in-flight candidate is discarded,
  never alerted.
- Duplicate alert prevention: the same selection is never pushed twice (event
  identity includes match, market, line, and odds snapshot).
- Odds snapshot staleness: alerts older than the freshness window are
  re-validated before sending or dropped.
- Rate limiting by Telegram: sends are queued with backoff; order preserved.
- Only the two authorized chat IDs can operate the bot; all other chats get a
  refusal message.
- Day-boundary handling uses Asia/Tehran consistently for `/stats` and record.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST monitor live matches across all configured sports on
  a continuous 24/7 schedule with automatic restart and state recovery.
- **FR-002**: System MUST evaluate every candidate market through the full
  analysis pipeline (de-vig, fair probability, edge vs second source,
  movement/sharp check, enrichment, written thesis, invalidation) before
  any alert.
- **FR-003**: System MUST classify qualified selections into exactly two
  tiers: obvious-edge and value, with distinct formatting and thresholds.
- **FR-004**: System MUST push alerts to all subscribed authorized chats
  within the latency budget and never duplicate an alert.
- **FR-005**: System MUST persist every selection with match, market, line,
  odds, timestamp, tier, thesis, and stake guidance.
- **FR-006**: System MUST settle selections to won/lost/void/pending and
  expose them via `/stats` (Tehran day) and `/record` (all-time).
- **FR-007**: System MUST support commands `/start`, `/help`,
  `/opportunities`, `/stats`, `/record`, `/subscribe`, `/unsubscribe`,
  `/settings`.
- **FR-008**: System MUST restrict all control and alert delivery to the
  configured authorized chat IDs.
- **FR-009**: System MUST organize monitored markets per sport against the
  1xBet reference taxonomy and report unpriceable markets as coverage gaps,
  never alerting on them.
- **FR-010**: System MUST corroborate every alert across at least two
  independent price sources and discard single-source outliers.
- **FR-011**: System MUST operate at $0 cost (free feeds/hosting only) and
  degrade gracefully instead of going offline when metered budgets exhaust.
- **FR-012**: System MUST respect source rate limits and Telegram send limits
  with queuing and backoff.
- **FR-013**: System MUST recommend only; it MUST NOT place bets or hold
  bookmaker credentials.
- **FR-014**: System MUST keep secrets (bot token, keys) out of code and
  logs, reading them from environment only.

### Key Entities

- **Selection**: A single recommended pick; attributes: match, sport, market
  type, line, odds snapshot, tier, thesis, invalidation, stake guidance,
  status (open/won/lost/void), timestamps. Related to Settlement and Alert.
- **Alert**: A delivered (or queued) notification of a Selection to a chat;
  attributes: selection reference, chat, sent/queued state, send timestamp.
- **Subscription**: Per-chat alert preferences; attributes: chat ID,
  subscribed flag, enabled tiers, quiet hours.
- **CoverageGap**: A market type declared unpriceable; attributes: sport,
  market type, reason, first/last observed dates.
- **DailyReport**: Aggregated view for one Tehran day; attributes: date,
  selections, outcome counts, tier breakdown.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A staged obvious-edge market produces correctly formatted
  alerts to both chats within 3 minutes of detection.
- **SC-002**: 100% of seeded settled selections for a day appear in
  `/stats` with correct outcomes and tally.
- **SC-003**: Zero alerts originate from single-source outliers or declared
  coverage gaps during soak testing.
- **SC-004**: Bot recovers from a forced restart with no lost persisted
  selections and resumes monitoring without manual steps.
- **SC-005**: 7-day continuous dry run completes with no crash requiring
  manual intervention and no spend above $0.
- **SC-006**: No duplicate alert for the same selection is ever delivered
  during soak testing.

## Assumptions

- Recipients have stable internet and Telegram access; hosting runs outside
  regions where required APIs are blocked.
- Free keyless feeds (ESPN scoreboard lines, Polymarket/Kalshi public APIs)
  remain available; Odds API key is an optional booster, never a dependency.
- The two authorized chat IDs are fixed for v1; adding recipients is a
  settings change, not a new feature.
- 1xBet market lineup is used as a taxonomy reference only; no 1xBet
  account, API, or scraping dependency exists.
- Flat capped stakes guidance only; no bankroll-percentage automation in v1.
- Tehran day boundary (Asia/Tehran) governs all daily reporting.
