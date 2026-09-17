/** fetch-based JSON GET. Mirrors bot/feeds/http.py (urllib -> fetch). */
import { BROWSER_UA } from "../config.ts";

export const FETCH_TIMEOUT_MS = 10000;

export async function getJson<T>(
  url: string,
  params?: Record<string, string>,
  userAgent: string = BROWSER_UA,
  timeoutMs: number = FETCH_TIMEOUT_MS,
): Promise<T> {
  let full = url;
  if (params && Object.keys(params).length > 0) {
    const qs = new URLSearchParams(params).toString();
    full += (url.includes("?") ? "&" : "?") + qs;
  }
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const resp = await fetch(full, {
      headers: { "User-Agent": userAgent, Accept: "application/json" },
      signal: ctrl.signal,
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status} for ${full}`);
    return (await resp.json()) as T;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * In-cycle response cache keyed by full URL. The monitor cycle refetches the
 * same Polymarket/ESPN URLs for many sports — cache keeps the cron
 * invocation well under the free-plan subrequest limit.
 */
export function cachedHttp(timeoutMs: number) {
  const cache = new Map<string, Promise<unknown>>();
  return {
    getJson<T>(url: string, params?: Record<string, string>, userAgent?: string): Promise<T> {
      let full = url;
      if (params && Object.keys(params).length > 0) {
        const qs = new URLSearchParams(params).toString();
        full += (url.includes("?") ? "&" : "?") + qs;
      }
      const key = `${userAgent ?? ""}|${full}`;
      let pending = cache.get(key) as Promise<T> | undefined;
      if (!pending) {
        pending = getJson<T>(url, params, userAgent, timeoutMs);
        // Failed fetches must not poison the cache for the rest of the cycle.
        pending.catch(() => cache.delete(key));
        cache.set(key, pending);
      }
      return pending;
    },
  };
}
