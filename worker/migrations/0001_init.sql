-- D1 schema. Mirrors bot/store.py (SQLite -> D1, same tables/columns).
CREATE TABLE IF NOT EXISTS selections (
    id TEXT PRIMARY KEY,
    sport TEXT NOT NULL,
    match_label TEXT NOT NULL,
    event_id TEXT NOT NULL,
    market_type TEXT NOT NULL,
    line TEXT,
    outcome TEXT NOT NULL,
    odds_decimal REAL NOT NULL,
    tier TEXT NOT NULL,
    edge REAL NOT NULL,
    ev REAL NOT NULL,
    stake_cap REAL NOT NULL,
    thesis TEXT NOT NULL,
    invalidation TEXT NOT NULL,
    sources TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    detected_at TEXT NOT NULL,
    settled_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sel_dedupe
    ON selections(event_id, market_type, line, outcome, status);
CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    selection_id TEXT NOT NULL REFERENCES selections(id),
    chat_id TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'queued',
    sent_at TEXT
);
CREATE TABLE IF NOT EXISTS subscriptions (
    chat_id TEXT PRIMARY KEY,
    subscribed INTEGER NOT NULL DEFAULT 1,
    tiers TEXT NOT NULL DEFAULT 'obvious,value',
    quiet_start TEXT,
    quiet_end TEXT
);
CREATE TABLE IF NOT EXISTS gaps (
    sport TEXT NOT NULL,
    market_type TEXT NOT NULL,
    reason TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    PRIMARY KEY (sport, market_type)
);
