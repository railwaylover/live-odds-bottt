# Live Odds Bot 🤖📈

24/7 Telegram bot that hunts mispriced **live** betting odds across all
sports and pushes tiered alerts (🟢 obvious edge / 🟡 value) with a written
thesis behind every pick — plus daily `/stats` won/lost tables.

- **Cost:** $0 — keyless feeds (ESPN, Polymarket, Kalshi), SQLite, free host
- **Accuracy rule:** every alert corroborated by ≥2 sources; unpriceable
  markets are reported as gaps, never alerted
- **Recommends only** — never places bets

## Run

```sh
cp .env.example .env   # TELEGRAM_BOT_TOKEN + AUTHORIZED_CHAT_IDS (never commit .env)
pip install -r requirements.txt
python -m bot.main
```

See `specs/001-live-odds-telegram-bot/quickstart.md` for validation.
Constitution: `.specify/memory/constitution.md`.
