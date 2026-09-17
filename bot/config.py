"""Live Odds Telegram Bot — settings from environment only. No secrets in code."""
from __future__ import annotations

import os
from datetime import timedelta, timezone
from zoneinfo import ZoneInfo

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

AUTHORIZED_CHAT_IDS = [
    c.strip() for c in os.environ.get("AUTHORIZED_CHAT_IDS", "").split(",") if c.strip()
]

DATA_DIR = os.environ.get("DATA_DIR", "data")
DB_PATH = os.path.join(DATA_DIR, "bot.db")

try:
    TEHRAN_TZ = ZoneInfo("Asia/Tehran")
except Exception:
    TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))  # Iran: UTC+3:30, no DST

# Edge thresholds (de-vigged edge, 0-1 scale)
OBVIOUS_EDGE = float(os.environ.get("OBVIOUS_EDGE", "0.06"))
VALUE_EDGE = float(os.environ.get("VALUE_EDGE", "0.025"))

# Stake guidance caps (flat units)
STAKE_CAP_OBVIOUS = float(os.environ.get("STAKE_CAP_OBVIOUS", "2.0"))
STAKE_CAP_VALUE = float(os.environ.get("STAKE_CAP_VALUE", "1.0"))

# Polling cadences (seconds)
LIVE_CADENCE = int(os.environ.get("LIVE_CADENCE", "90"))
PREMATCH_CADENCE = int(os.environ.get("PREMATCH_CADENCE", "1800"))

# Freshness: odds snapshot older than this is re-validated before alerting
FRESHNESS_WINDOW = int(os.environ.get("FRESHNESS_WINDOW", "300"))

# Minimum market volume (in source-native units) to trust a price
MIN_VOLUME = float(os.environ.get("MIN_VOLUME", "100"))

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120 Safari/537.36"
)
