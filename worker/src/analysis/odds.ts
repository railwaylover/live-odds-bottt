/** Odds math. Exact port of bot/analysis/odds.py (same formulas). */

export function americanToDecimal(odds: number): number {
  const o = Number(odds);
  if (o > 0) return 1 + o / 100;
  return 1 + 100 / Math.abs(o);
}

export function decimalToProb(decimalOdds: number): number {
  return 1 / Number(decimalOdds);
}

export function probToDecimal(prob: number): number {
  return 1 / Number(prob);
}

/** Remove overround by normalizing implied probabilities (multiplicative). */
export function devig(decimalOdds: number[]): number[] {
  const implied = decimalOdds.map(decimalToProb);
  const total = implied.reduce((a, b) => a + b, 0);
  if (!(total > 0)) throw new Error("invalid odds for de-vigging");
  return implied.map((p) => p / total);
}

/** Edge of a price vs fair probability: fair - implied. */
export function edge(fairProb: number, marketDecimal: number): number {
  return fairProb - decimalToProb(marketDecimal);
}

/** EV per unit staked. */
export function expectedValue(fairProb: number, marketDecimal: number): number {
  return fairProb * marketDecimal - 1;
}

export function kellyFraction(fairProb: number, marketDecimal: number): number {
  const b = marketDecimal - 1;
  if (!(b > 0)) return 0;
  const q = 1 - fairProb;
  const f = (b * fairProb - q) / b;
  return Math.max(0, f);
}

/** Half-Kelly stake suggestion bounded by the tier cap. */
export function kellyLite(fairProb: number, marketDecimal: number, cap: number): number {
  return Math.round(Math.min(kellyFraction(fairProb, marketDecimal) / 2, cap) * 100) / 100;
}
