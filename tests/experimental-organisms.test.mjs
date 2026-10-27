import test from "node:test";
import assert from "node:assert/strict";
import { TemporalEchoRule, VacuumLeech } from "../apps/manifold_reactor/experimental-organisms.mjs";

test("temporal echo waits until residual amplitude crosses configured threshold", () => {
  const rule = new TemporalEchoRule({ decayRate: Math.log(2), minResidual: 0.5 });
  const crystal = { id: "c1", birthEpoch: 0, vector: [1, 1] };
  assert.equal(rule.evaluate(crystal, 0), null);
  assert.equal(rule.evaluate(crystal, 1), null);
  const echo = rule.evaluate(crystal, 2);
  assert.ok(echo);
  assert.equal(echo.originId, "c1");
  assert.ok(Math.abs(echo.phaseShift - Math.PI / 4) < 1e-12);
  assert.ok(echo.amplitude > 0.5 && echo.amplitude < 1);
  assert.ok(Object.isFrozen(echo));
});

test("echo cache is stable within an epoch, bounded, and expires", () => {
  const rule = new TemporalEchoRule({
    decayRate: 1,
    minResidual: 0.9,
    maxCacheEntries: 2,
    cacheTtlEpochs: 2,
  });
  const crystal = (id) => ({ id, birthEpoch: 0, vector: [1, 0] });
  const first = rule.evaluate(crystal("a"), 1);
  assert.equal(rule.evaluate(crystal("a"), 1), first);
  rule.evaluate(crystal("b"), 1);
  rule.evaluate(crystal("c"), 1);
  assert.equal(rule.phantomCache.size, 2);
  rule.prune(10);
  assert.equal(rule.phantomCache.size, 0);
  rule.evaluate(crystal("d"), 1);
  rule.clear();
  assert.equal(rule.phantomCache.size, 0);
});

test("temporal echo rejects invalid input and future epochs", () => {
  const rule = new TemporalEchoRule();
  assert.throws(() => rule.evaluate(null, 1), TypeError);
  assert.throws(() => rule.evaluate({ id: "x", birthEpoch: 2, vector: [0, 1] }, 1), RangeError);
  assert.throws(() => new TemporalEchoRule({ minResidual: 1 }), RangeError);
  assert.throws(() => new TemporalEchoRule({ maxCacheEntries: 0 }), RangeError);
});

test("vacuum leech uses initial load as fallback and caps drain per tick", () => {
  const leech = new VacuumLeech({
    id: "leech-1",
    initialBandwidthLoad: 1000,
    siphonRate: 0.042,
    activationThreshold: 800,
    maxDrainPerTick: 20,
  });
  assert.equal(leech.perception({}), 1000);
  assert.equal(leech.action(800).type, "DORMANT");
  const action = leech.action(leech.perception({ subspaceBandwidth: 1000 }));
  assert.equal(action.type, "SIPHON_ENERGY");
  assert.equal(action.drain, 20);
  assert.equal(action.target, "SOL-3-GATE");
  assert.ok(Object.isFrozen(action));
});

test("neutralized leech stays dormant and invalid loads are rejected", () => {
  const leech = new VacuumLeech({ id: "leech-2" });
  const result = leech.neutralize();
  assert.equal(result.type, "NEUTRALIZED");
  assert.equal(leech.action(5000).type, "DORMANT");
  assert.throws(() => leech.perception({ subspaceBandwidth: -1 }), RangeError);
  assert.throws(() => leech.action(Infinity), TypeError);
  assert.throws(() => new VacuumLeech({ id: "" }), TypeError);
});
