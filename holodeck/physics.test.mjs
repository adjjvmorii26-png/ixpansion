import test from "node:test";
import assert from "node:assert/strict";
import { World, LIMITS } from "./physics.mjs";

test("gravity advances position on a fixed step", () => {
  const w = new World({ gravity: 10, width: 400, height: 300 });
  const id = w.addBody({ x: 100, y: 50, vx: 0, vy: 0, mass: 2, radius: 5 });
  w.step(0.01);
  const b = w.bodies.find(x => x.id === id);
  assert.ok(b.y > 50);
  assert.ok(Math.abs(b.vy - 0.1) < 1e-12);
});
test("gravity and mass reject non-finite or out-of-range values", () => {
  const w = new World();
  assert.throws(() => w.setGravity(NaN), /finite/);
  assert.throws(() => w.setGravity(100), /range/);
  assert.throws(() => w.addBody({ mass: LIMITS.mass[1] + 1 }), /mass/);
  assert.throws(() => w.step(1), /dt/);
});
test("snapshot restore preserves state and deterministic hash", () => {
  const a = new World({ gravity: 3, width: 500, height: 400 });
  a.addBody({ x: 200, y: 60, vx: 2, vy: -1, mass: 4, radius: 9 });
  for (let i = 0; i < 20; i++) a.step(1 / 120);
  const snapshot = a.snapshot();
  const b = new World();
  b.restore(snapshot);
  assert.equal(a.stateHash(), b.stateHash());
  a.step(1 / 120); b.step(1 / 120);
  assert.equal(a.stateHash(), b.stateHash());
});
test("branches remain isolated after restoring the same snapshot", () => {
  const base = new World();
  base.addBody({ x: 100, y: 100 });
  const snapshot = base.snapshot();
  const normal = new World(); normal.restore(snapshot);
  const zero = new World(); zero.restore(snapshot); zero.setGravity(0);
  for (let i = 0; i < 60; i++) { normal.step(); zero.step(); }
  assert.notEqual(normal.stateHash(), zero.stateHash());
  assert.equal(base.tick, 0);
});
test("body capacity is bounded", () => {
  const w = new World();
  for (let i = 0; i < LIMITS.maxBodies; i++) w.addBody();
  assert.throws(() => w.addBody(), /capacity/);
});
