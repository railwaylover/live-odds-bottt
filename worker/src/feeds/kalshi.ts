/** Kalshi public trade API client (no auth for reads). Mirrors bot/feeds/kalshi.py. */
import type { Http, LiveEvent, Source } from "./base.ts";

const API = "https://api.elections.kalshi.com/trade-api/v2";

export const SERIES: Record<string, string> = {
  nba: "KXNBA",
  nfl: "KXNFL",
  mlb: "KXMLB",
  nhl: "KXNHL",
  "soccer-epl": "KXEPL",
  "soccer-ucl": "KXUCL",
  "soccer-laliga": "KXLALIGA",
  "soccer-bundesliga": "KXBUNDESLIGA",
  "soccer-seriea": "KXSERIEA",
  "soccer-ligue1": "KXLIGUE1",
  "tennis-atp": "KXATP",
};

interface KalshiMarket {
  ticker?: string;
  event_ticker?: string;
  title?: string;
  yes_bid?: number;
  last_price?: number;
  volume?: number;
}

export class KalshiSource implements Source {
  readonly name = "kalshi";

  async fetchLive(sport: string, http: Http): Promise<LiveEvent[]> {
    const ticker = SERIES[sport];
    if (!ticker) return [];
    let data: { markets?: KalshiMarket[] };
    try {
      data = await http.getJson<{ markets?: KalshiMarket[] }>(`${API}/markets`, {
        series_ticker: ticker,
        status: "open",
        limit: "100",
      });
    } catch {
      return [];
    }
    const events: LiveEvent[] = [];
    for (const m of data.markets ?? []) {
      try {
        const yes = Number(m.yes_bid ?? m.last_price ?? 0);
        const no = yes ? 100 - yes : 0;
        if (!(yes > 0) || !(yes < 100)) continue;
        const volume = Number(m.volume ?? 0) || 0;
        events.push({
          eventId: `kalshi-${m.ticker}`,
          sport,
          matchLabel: m.title ?? m.event_ticker ?? "?",
          isLive: true,
          markets: [
            {
              marketType: "moneyline",
              line: null,
              outcomes: [
                { name: "yes", decimalOdds: 100 / yes, volume },
                { name: "no", decimalOdds: 100 / no, volume },
              ],
            },
          ],
          rawScore: "",
        });
      } catch {
        continue;
      }
    }
    return events;
  }
}
