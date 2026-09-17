# Quickstart: Live Odds Telegram Bot

Validates the feature end to end without spending money or placing bets.

## Prerequisites

- Python 3.10+
- `pip install -r requirements.txt`
- A Telegram bot token in env `TELEGRAM_BOT_TOKEN` (test bot is fine)
- Your chat ID in env `AUTHORIZED_CHAT_IDS` (comma-separated)

## Run

```sh
cp .env.example .env   # fill in token + chat IDs, never commit .env
python -m bot.main
```

Send `/start` to the bot. Expect the welcome message.

## Validate user stories

1. **US1/US2 alerts**: `python scripts/stage_fixture.py --tier obvious`
   stages a known mispriced market; both chats MUST receive the tiered alert
   within 3 minutes. Repeat with `--tier value`.
2. **No-duplicate/no-outlier**: re-run the stager; no second alert may arrive.
   Stage a single-source outlier; no alert may arrive.
3. **US3 stats**: `python scripts/seed_results.py --date today` then send
   `/stats`; every seeded pick MUST appear with the correct ✅/❌/➖/⏳
   marker and tally. Send `/record` for the all-time view.
4. **US4 coverage**: send `/coverage`; the staged market type is listed as
   monitored, the deliberately unpriceable one as a gap.
5. **US5 commands**: exercise `/opportunities`, `/subscribe`,
   `/unsubscribe`, `/settings`; verify state changes and quiet-hour queueing.
6. **Resilience**: kill and restart the process; selections persist and
   monitoring resumes with no manual steps.

## Tests

```sh
python -m pytest tests/ -q
```

All tests MUST pass. See `contracts/commands.md` for message formats and
`data-model.md` for entity rules under test.
