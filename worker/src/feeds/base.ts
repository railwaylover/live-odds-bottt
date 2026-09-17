/** Feed interface + normalized event model. Mirrors bot/feeds/base.py. */

export interface OutcomePrice {
  name: string;
  decimalOdds: number;
  /** Source-native units; 0 = unknown. */
  volume: number;
}

export interface MarketPrice {
  marketType: string;
  line: string | null;
  outcomes: OutcomePrice[];
}

export interface LiveEvent {
  eventId: string;
  sport: string;
  matchLabel: string;
  isLive: boolean;
  markets: MarketPrice[];
  rawScore: string;
  sourceName?: string;
}

export interface FinalsMap {
  [eventId: string]: { home: number; away: number };
}

export interface Source {
  readonly name: string;
  fetchLive(sport: string, http: Http): Promise<LiveEvent[]>;
  fetchFinals?(http: Http): Promise<FinalsMap>;
}

/** Shared fetch helper with per-source User-Agent + timeout. */
export interface Http {
  getJson<T>(url: string, params?: Record<string, string>, userAgent?: string): Promise<T>;
}
