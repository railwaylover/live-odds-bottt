/**
 * Per-sport market catalog vs 1xBet taxonomy.
 * Content mirrors bot/catalog/markets.yaml (true = monitored, false = gap).
 * Embedded as a constant: Workers have no filesystem for the YAML file.
 */
const CATALOG: Record<string, Record<string, boolean>> = {
  "soccer-epl": {
    "1x2": true, "double-chance": true, total: true, handicap: true,
    "1st-half-1x2": true, "1st-half-total": true, "team-to-score-1st-half": false,
    btts: true, "cards-total": false, "corners-total": false,
  },
  "soccer-laliga": {
    "1x2": true, "double-chance": true, total: true, handicap: true,
    "1st-half-1x2": true, "1st-half-total": true, "team-to-score-1st-half": false,
    btts: true, "cards-total": false, "corners-total": false,
  },
  "soccer-bundesliga": {
    "1x2": true, total: true, handicap: true, btts: true,
    "cards-total": false, "corners-total": false,
  },
  "soccer-seriea": {
    "1x2": true, total: true, handicap: true, btts: true,
    "cards-total": false, "corners-total": false,
  },
  "soccer-ligue1": {
    "1x2": true, total: true, handicap: true, btts: true,
    "cards-total": false, "corners-total": false,
  },
  "soccer-ucl": {
    "1x2": true, total: true, handicap: true, btts: true,
    "cards-total": false, "corners-total": false,
  },
  nba: { moneyline: true, spread: true, total: true, "1st-half-spread": true, "1st-half-total": true },
  nfl: { moneyline: true, spread: true, total: true, "1st-half-spread": true },
  mlb: { moneyline: true, "run-line": true, total: true },
  nhl: { moneyline: true, "puck-line": true, total: true },
  "tennis-atp": { moneyline: true, "set-handicap": true, "total-games": true },
};

export function isMonitored(sport: string, marketType: string): boolean {
  return CATALOG[sport]?.[marketType] === true;
}

export function monitoredMarkets(sport: string): string[] {
  const entry = CATALOG[sport] ?? {};
  return Object.keys(entry).filter((m) => entry[m]);
}

export function allSports(): string[] {
  return Object.keys(CATALOG).sort();
}
