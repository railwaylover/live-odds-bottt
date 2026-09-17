# Data Model: Live Odds Telegram Bot

**Feature**: `001-live-odds-telegram-bot` | **Date**: 2026-09-17

## Entities

### Selection

A single recommended pick. The unit of record for alerts and statistics.

| Field | Type | Rules |
|---|---|---|
| id | string (uuid) | unique, immutable |
| sport | string | e.g. `soccer-epl`, `nba`; required |
| match_label | string | e.g. "Arsenal vs Chelsea"; required |
| event_id | string | source event identifier; required |
| market_type | string | 1xBet-taxonomy code, e.g. `1x2`, `total-over-under`, `handicap`, `1st-half-goal`; required |
| line | string/nullable | e.g. `2.5`, `NULL` for moneyline |
| outcome | string | the recommended side; required |
| odds_decimal | float | snapshot at detection; > 1.0, required |
| tier | enum | `obvious` \| `value`; required |
| edge | float | de-vigged edge 0–1; required |
| ev | float | expected value per unit stake; required |
| stake_cap | float | max suggested units; required, > 0 |
| thesis | string | written justification; required, non-empty |
| invalidation | string | what kills the thesis; required |
| sources | string list | ≥ 2 corroborating sources; required |
| status | enum | `open` → `won` \| `lost` \| `void`; `pending` if unsettlable; default `open` |
| detected_at | datetime UTC | required |
| settled_at | datetime UTC/nullable | set on settlement |

Identity: `(event_id, market_type, line, outcome)` unique among `open`
selections — enforces no-duplicate alerts.

### Alert

A delivery record of a Selection to a chat.

| Field | Type | Rules |
|---|---|---|
| id | string (uuid) | unique |
| selection_id | ref Selection | required |
| chat_id | string | required, must be authorized |
| state | enum | `queued` → `sent` \| `failed`; required |
| sent_at | datetime UTC/nullable | set on send |

### Subscription

Per-chat alert preferences.

| Field | Type | Rules |
|---|---|---|
| chat_id | string | primary key, authorized list only |
| subscribed | bool | default true |
| tiers | enum list | subset of `obvious`, `value`; default both |
| quiet_start/quiet_end | time/nullable | Tehran wall-clock; NULL = no quiet hours |

### CoverageGap

A market type declared unpriceable.

| Field | Type | Rules |
|---|---|---|
| sport | string | required |
| market_type | string | required |
| reason | string | e.g. `no-reliable-feed`; required |
| first_seen/last_seen | date | required |

Uniqueness: `(sport, market_type)`.

### DailyReport (derived, not stored)

Aggregated per Tehran-day view over Selections: date, counts by
`won/lost/void/pending`, tier breakdown. Computed on demand for `/stats`.

## State transitions

- Selection: `open` → `won` | `lost` | `void` (feed settlement);
  `open` → `pending` when unsettlable; `pending` → terminal when resolved.
  Terminal states are final.
- Alert: `queued` → `sent` | `failed`; `failed` retries with backoff, then
  stays `failed` with error logged.
