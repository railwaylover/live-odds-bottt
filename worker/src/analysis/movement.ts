/** Line-movement classification. Port of bot/analysis/movement.py. */
export type Movement = "stable" | "steam" | "sharp" | "drift";

export function classify(openProb: number, currentProb: number): Movement {
  const ad = Math.abs(currentProb - openProb);
  if (ad < 0.03) return "stable";
  if (ad >= 0.1) return "steam";
  if (ad >= 0.05) return "sharp";
  return "drift";
}
