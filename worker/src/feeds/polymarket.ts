/** Polymarket Gamma API client (keyless, browser UA required). Mirrors bot/feeds/polymarket.py. */
import type { Http, LiveEvent, MarketPrice, OutcomePrice, Source } from "./base.ts";

const GAMMA = "https://gamma-api.polymarket.com";

interface GammaMarket {
  outcomes?: string | string[];
  outcomePrices?: string | string[];
  volume?: string | number;
}
interface GammaEvent {
  id?: string | number;
  title?: string;
  markets?: GammaMarket[];
}

function asArray(v: string | string[] | undefined): string[] {
  if (!v) return [];
  if (Array.isArray(v)) return v;
  try {
    const parsed = JSON.parse(v) as unknown;
    return Array.isArray(parsed) ? parsed.map(String) : [];
  } catch {
    return [];
  }
}

export class PolymarketSource implements Source {
  readonly name = "polymarket";

  async fetchLive(sport: string, http: Http): Promise<LiveEvent[]> {
    // No keyword prefilter: matching to fixtures happens in monitor.ts
    // via team-token overlap (same as the Python bot).
    let data: GammaEvent[];
    try {
      data = await http.getJson<GammaEvent[]>(`${GAMMA}/events`, { closed: "false", limit: "150" });
    } catch {
      return [];
    }
    const events: LiveEvent[] = [];
    for (const ev of data ?? []) {
      const markets: MarketPrice[] = [];
      for (const m of ev.markets ?? []) {
        try {
          const outcomes = asArray(m.outcomes);
          const prices = asArray(m.outcomePrices);
          if (outcomes.length === 0 || prices.length === 0) continue;
          const volume = Number(m.volume ?? 0) || 0;
          const ops: OutcomePrice[] = [];
          for (let i = 0; i < Math.min(outcomes.length, prices.length); i++) {
            const p = Number(prices[i]);
            if (!(p > 0)) continue;
            ops.push({ name: String(outcomes[i]), decimalOdds: 1 / p, volume });
          }
          if (ops.length >= 2) markets.push({ marketType: "moneyline", line: null, outcomes: ops });
        } catch {
          continue;
        }
      }
      if (markets.length > 0) {
        events.push({
          eventId: `poly-${ev.id}`,
          sport,
          matchLabel: ev.title ?? "?",
          isLive: true,
          markets,
          rawScore: "",
        });
      }
    }
    return events;
  }
}
