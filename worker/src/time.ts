/** Tehran wall-clock helpers. Primary: Intl Asia/Tehran; fallback: UTC+3:30. */

const TEHRAN_OFFSET_MINUTES = 3 * 60 + 30; // Iran: UTC+3:30, no DST

function tehranParts(date: Date): { y: string; m: string; d: string; hm: string } | null {
  try {
    const fmt = new Intl.DateTimeFormat("en-CA", {
      timeZone: "Asia/Tehran",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hourCycle: "h23",
    });
    const parts = Object.fromEntries(
      fmt.formatToParts(date).map((p) => [p.type, p.value]),
    );
    return { y: parts["year"]!, m: parts["month"]!, d: parts["day"]!, hm: `${parts["hour"]}:${parts["minute"]}` };
  } catch {
    return null;
  }
}

/** YYYY-MM-DD in Tehran for the given instant (default: now). */
export function tehranDay(date: Date = new Date()): string {
  const p = tehranParts(date);
  if (p) return `${p.y}-${p.m}-${p.d}`;
  const t = new Date(date.getTime() + TEHRAN_OFFSET_MINUTES * 60_000);
  return t.toISOString().slice(0, 10);
}

/** HH:MM in Tehran for the given instant (default: now). */
export function tehranClock(date: Date = new Date()): string {
  const p = tehranParts(date);
  if (p) return p.hm;
  const t = new Date(date.getTime() + TEHRAN_OFFSET_MINUTES * 60_000);
  return t.toISOString().slice(11, 16);
}

/** Tehran day of an ISO UTC timestamp stored in the DB. */
export function tehranDayOf(isoUtc: string): string {
  return tehranDay(new Date(isoUtc));
}

export function utcNowIso(): string {
  return new Date().toISOString();
}
