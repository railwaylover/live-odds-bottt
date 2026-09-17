import { describe, it } from "node:test";
import assert from "node:assert/strict";
import type { LiveEvent } from "../src/feeds/base.ts";
import { sameMatch } from "../src/monitor.ts";

function ev(label: string): LiveEvent {
  return { eventId: "1", sport: "x", matchLabel: label, isLive: true, markets: [], rawScore: "" };
}

describe("sameMatch", () => {
  it("joins cross-source titles", () => {
    assert.equal(sameMatch(ev("Toronto Raptors vs Miami Heat"), ev("Raptors vs Heat - Winner?")), true);
  });

  it("does not join same-city teams", () => {
    assert.equal(
      sameMatch(ev("Toronto Maple Leafs vs Montreal Canadiens"), ev("Toronto Raptors vs Miami Heat")),
      false,
    );
  });

  it("does not join unrelated fixtures", () => {
    assert.equal(sameMatch(ev("Buffalo Bills vs Detroit Lions"), ev("Real Betis vs Getafe")), false);
  });

  it("joins identical labels", () => {
    assert.equal(sameMatch(ev("Arsenal vs Chelsea"), ev("Arsenal vs Chelsea")), true);
  });
});
