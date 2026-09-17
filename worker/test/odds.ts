import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { americanToDecimal, decimalToProb, devig, edge, expectedValue, kellyLite } from "../src/analysis/odds.ts";

describe("odds", () => {
  it("converts american odds", () => {
    assert.ok(Math.abs(americanToDecimal(-110) - 1.909) < 0.001);
    assert.equal(americanToDecimal(150), 2.5);
  });

  it("de-vigs to normalized probabilities", () => {
    const fair = devig([1.9, 1.9]);
    assert.ok(Math.abs(fair[0]! + fair[1]! - 1) < 1e-9);
    assert.ok(Math.abs(fair[0]! - 0.5) < 1e-9);
  });

  it("computes positive edge and EV", () => {
    assert.ok(Math.abs(edge(0.6, 2.0) - 0.1) < 1e-9);
    assert.ok(Math.abs(expectedValue(0.6, 2.0) - 0.2) < 1e-9);
  });

  it("caps kelly-lite stakes", () => {
    assert.ok(kellyLite(0.9, 10.0, 2.0) <= 2.0);
    assert.equal(kellyLite(0.1, 1.5, 1.0), 0);
  });

  it("round-trips probability conversion", () => {
    assert.ok(Math.abs(decimalToProb(2.5) - 0.4) < 1e-9);
  });
});
