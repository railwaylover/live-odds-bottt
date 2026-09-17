# Live Odds Bot — Cloudflare Workers Deployment

Webhook-based port of the Python Telegram bot (`../bot/`) for Cloudflare
Workers. **No features removed**: all 9 commands, both alert tiers,
2-source corroboration, fuzzy fixture matching, settlement, gap reporting,
quiet hours, and Tehran-day stats behave exactly as in the Python version.

## Why this shape (architecture decisions)

| Python (VPS) | Workers equivalent | Reason |
|---|---|---|
| `python-telegram-bot` long-polling | `fetch` webhook handler (`src/index.ts`) + Telegram `secret_token` check | Workers have no sockets or background processes |
| `while True` monitor loop | Cron Trigger `*/2 * * * *` → `scheduled()` runs one bounded cycle | Same logic (`src/monitor.ts`), driven by cron |
| SQLite file (`bot.db`) | D1 database (SQLite-compatible, same schema in `migrations/`) | No filesystem on Workers |
| `asyncio` fan-out | Bounded promise pool (8 concurrent) + per-cycle URL cache | Stays under the free-plan subrequest limit |
| `pip install` deps | Zero runtime deps (only `fetch`, `Intl`, `crypto`) | Small, fast cold starts |

Python is intentionally **not** used on Workers: Python Workers run on
Pyodide without TCP sockets, so `python-telegram-bot` cannot work there.
TypeScript + raw Bot API calls is the production-ready path.

## Prerequisites

- Cloudflare account (free plan works) + `wrangler` CLI (`npm i -g wrangler`)
- The repo cloned locally; `cd worker`

## Setup (production)

1. **Create the D1 database and apply the schema**
   ```sh
   wrangler d1 create live-odds-bot
   # copy the returned database_id into wrangler.toml
   wrangler d1 migrate local --local   # dry run (optional)
   wrangler d1 migrations apply live-odds-bot --remote
   ```

2. **Set secrets (never in code or git)**
   ```sh
   wrangler secret put TELEGRAM_BOT_TOKEN   # fresh BotFather token
   wrangler secret put WEBHOOK_SECRET       # long random string you invent
   ```
   Non-secret vars (`AUTHORIZED_CHAT_IDS`, thresholds) live in
   `wrangler.toml` `[vars]`.

3. **Deploy**
   ```sh
   npm install
   npm run typecheck && npm test
   wrangler deploy   # note the https://live-odds-bot.<you>.workers.dev URL
   ```

4. **Register the webhook with Telegram** (replace placeholders)
   ```sh
   curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
     -H 'Content-Type: application/json' \
     -d '{"url":"https://live-odds-bot.<you>.workers.dev/",
          "secret_token":"YOUR_WEBHOOK_SECRET",
          "allowed_updates":["message"]}'
   ```
   Expect `{"ok":true,...}`. Verify: `.../getWebhookInfo` shows the URL
   and no `last_error_message`.

5. **Send `/start`** to the bot. The cron runs the monitor every 2 minutes;
   watch it with `wrangler tail`.

## Environment reference

| Name | Kind | Required | Purpose |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | secret | yes | Bot API token (fresh, never chat-exposed) |
| `WEBHOOK_SECRET` | secret | yes | Validated against Telegram's `secret_token` header |
| `AUTHORIZED_CHAT_IDS` | var | yes | Comma-separated chat IDs allowed to use the bot |
| `OBVIOUS_EDGE` / `VALUE_EDGE` | var | no | Tier thresholds (defaults `0.06` / `0.025`) |
| `STAKE_CAP_OBVIOUS` / `STAKE_CAP_VALUE` | var | no | Stake caps (defaults `2.0` / `1.0`) |
| `MIN_VOLUME` | var | no | Min market volume (default `100`) |
| `FETCH_TIMEOUT_MS` | var | no | Per-feed timeout (default `10000`) |
| `DB` | D1 binding | yes | `live-odds-bot` database |

## Commands (unchanged)

`/start /help /opportunities /stats [YYYY-MM-DD] /record /coverage
/subscribe [obvious|value|all] /unsubscribe /settings` — same texts and
auth gate (`⛔ This bot is private.`) as the Python bot.

## Free-plan limits to know

- **Cron minimum is 1 minute**; this project uses every 2 minutes.
- **50 subrequests/invocation**: the in-cycle URL cache (Polymarket and
  ESPN finals reuse) keeps a full all-sports cycle around ~25 fetches.
- **10 ms CPU/invocation**: fetches are I/O (don't count); JSON parsing
  per cycle is small. If Telegram sends burst, each update is cheap.
- **D1 free**: 5 GB + 5M reads/day — this bot's volume is far below that.

## Parity notes (deliberate, documented)

- `quiet hours → queued` alerts are recorded as `queued` exactly like the
  Python bot (no retroactive flush in either version).
- `medianFair` helper is ported but, as in Python, reserved for tooling.
- `PREMATCH_CADENCE`/`FRESHNESS_WINDOW` exist in Python config but the
  cron cadence supersedes them here; thresholds and volume rules are
  identical.

## Local verification (no Cloudflare account needed)

```sh
npm install
npm run typecheck   # tsc --noEmit
npm test            # 23 unit tests; store tests run the REAL migration
                    # SQL against SQLite via a D1-compatible shim
```
