import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { formatAlert, formatRecord, formatStats, inQuietHours } from "../src/notify.ts";
import { settle, settle1x2, settleTotal } from "../src/settle.ts";

function sel() {
  return {
    sport: "nba",
    match_label: "A vs B",
    market_type: "moneyline",
    line: null,
    outcome: "home",
    odds_decimal: 2.1,
    tier: "obvious",
    edge: 0.08,
    ev: 0.17,
    stake_cap: 2.0,
    thesis: "fair vs market",
    invalidation: "drift",
    status: "open",
  };
}

describe("notify", () => {
  it("alert contains all required fields", () => {
    const text = formatAlert(sel());
    for (const needle of ["A vs B", "2.1", "Thesis:", "Invalid if:", "🟢"]) {
      assert.ok(text.includes(needle), `missing ${needle}`);
    }
  });

  it("stats renders empty and full reports", () => {
    assert.ok(formatStats({ day: "2026-01-01", picks: [], counts: {} }).includes("No selections"));
    const text = formatStats({
      day: "2026-01-01",
      picks: [{ ...sel(), status: "won" }],
      counts: { won: 1, lost: 0, void: 0, pending: 0 },
    });
    assert.ok(text.includes("✅") && text.includes("Tally"));
  });

  it("record renders rows", () => {
    assert.ok(formatRecord([]).includes("No settled"));
    assert.ok(formatRecord([{ tier: "obvious", status: "won", count: 2 }]).includes("obvious"));
  });

  it("handles overnight quiet hours", () => {
    const sub = { quiet_start: "22:00", quiet_end: "07:00" };
    // 23:00 and 12:00 Tehran on fixed dates (Tehran = UTC+3:30, no DST).
    assert.equal(inQuietHours(sub, new Date("2026-01-01T19:30:00Z")), true);
    assert.equal(inQuietHours(sub, new Date("2026-01-01T08:30:00Z")), false);
  });
});

describe("settle", () => {
  it("settles 1x2 including draws", () => {
    assert.equal(settle1x2({ market_type: "1x2", outcome: "draw", line: null }, { home: 1, away: 1 }), "won");
    assert.equal(settle1x2({ market_type: "moneyline", outcome: "home", line: null }, { home: 2, away: 1 }), "won");
    assert.equal(settle1x2({ market_type: "moneyline", outcome: "home", line: null }, { home: 0, away: 1 }), "lost");
    assert.equal(settle1x2({ market_type: "moneyline", outcome: "home", line: null }, null), "pending");
  });

  it("settles totals including pushes", () => {
    assert.equal(settleTotal({ market_type: "total", outcome: "over", line: "2.5" }, { home: 2, away: 1 }), "won");
    assert.equal(settleTotal({ market_type: "total", outcome: "over", line: "2.5" }, { home: 1, away: 0 }), "lost");
    assert.equal(settleTotal({ market_type: "total", outcome: "over", line: "3.0" }, { home: 2, away: 1 }), "void");
  });

  it("never guesses exotics", () => {
    assert.equal(settle({ market_type: "cards-total", outcome: "over", line: "3.5" }, { home: 2, away: 1 }), "pending");
  });
});
