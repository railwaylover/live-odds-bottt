/** Feed-driven settlement. Port of bot/settle.py — never guesses. */

export interface FinalScore {
  home: number;
  away: number;
}

export interface SettleSelection {
  market_type: string;
  outcome: string;
  line: string | null;
}

export function settle1x2(selection: SettleSelection, final: FinalScore | null): string {
  if (!final || final.home === undefined || final.away === undefined) return "pending";
  const { home, away } = final;
  const outcome = (selection.outcome || "").toLowerCase();
  const winner = home === away ? "draw" : home > away ? "home" : "away";
  if (outcome === "yes" || outcome === "no") return "pending"; // prediction-market semantics need market-specific logic
  return outcome === winner ? "won" : "lost";
}

export function settleTotal(selection: SettleSelection, final: FinalScore | null): string {
  if (!final || selection.line === null || selection.line === undefined) return "pending";
  const total = final.home + final.away;
  const line = Number(selection.line);
  if (!Number.isFinite(total) || !Number.isFinite(line)) return "pending";
  const outcome = (selection.outcome || "").toLowerCase();
  if (total === line) return "void";
  const isOver = total > line;
  if (outcome.startsWith("over") || outcome === "yes") return isOver ? "won" : "lost";
  if (outcome.startsWith("under") || outcome === "no") return !isOver ? "won" : "lost";
  return "pending";
}

export function settle(selection: SettleSelection, final: FinalScore | null): string {
  const mt = (selection.market_type || "").toLowerCase();
  if (mt === "moneyline" || mt === "1x2") return settle1x2(selection, final);
  if (mt.startsWith("total")) return settleTotal(selection, final);
  return "pending"; // exotic markets: explicit logic per type, never guessed
}
