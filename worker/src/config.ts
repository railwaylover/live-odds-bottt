/** Settings from Worker vars/secrets only. No secrets in code. Mirrors bot/config.py. */

export interface Env {
  TELEGRAM_BOT_TOKEN: string;
  AUTHORIZED_CHAT_IDS: string;
  /** Validated against Telegram's X-Telegram-Bot-Api-Secret-Token header. */
  WEBHOOK_SECRET: string;
  OBVIOUS_EDGE?: string;
  VALUE_EDGE?: string;
  STAKE_CAP_OBVIOUS?: string;
  STAKE_CAP_VALUE?: string;
  MIN_VOLUME?: string;
  FETCH_TIMEOUT_MS?: string;
  DB: D1Database;
}

export interface Settings {
  botToken: string;
  authorizedChatIds: string[];
  obviousEdge: number;
  valueEdge: number;
  stakeCapObvious: number;
  stakeCapValue: number;
  minVolume: number;
  fetchTimeoutMs: number;
}

function num(value: string | undefined, fallback: number): number {
  const n = value === undefined || value === "" ? NaN : Number(value);
  return Number.isFinite(n) ? n : fallback;
}

export function settings(env: Env): Settings {
  return {
    botToken: env.TELEGRAM_BOT_TOKEN ?? "",
    authorizedChatIds: (env.AUTHORIZED_CHAT_IDS ?? "")
      .split(",")
      .map((c) => c.trim())
      .filter(Boolean),
    obviousEdge: num(env.OBVIOUS_EDGE, 0.06),
    valueEdge: num(env.VALUE_EDGE, 0.025),
    stakeCapObvious: num(env.STAKE_CAP_OBVIOUS, 2.0),
    stakeCapValue: num(env.STAKE_CAP_VALUE, 1.0),
    minVolume: num(env.MIN_VOLUME, 100),
    fetchTimeoutMs: num(env.FETCH_TIMEOUT_MS, 10000),
  };
}

/** Neutral client UA (ESPN's WAF blocks browser-like UAs). Mirrors ESPN_UA. */
export const ESPN_UA = "live-odds-bot/1.0 (+https://github.com/)";

/** Browser UA (Polymarket Gamma requires it). Mirrors config.USER_AGENT. */
export const BROWSER_UA =
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 " +
  "(KHTML, like Gecko) Chrome/120 Safari/537.36";
