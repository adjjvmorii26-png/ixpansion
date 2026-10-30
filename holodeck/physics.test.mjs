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

test("restore rejects duplicate ids without mutating the live world", () => {
  const w = new World({ gravity: 4 });
  w.addBody({ x: 100, y: 120 });
  w.step();
  const before = w.stateHash();
  const bad = w.snapshot();
  bad.bodies.push({ ...bad.bodies[0] });
  bad.nextId += 1;
  assert.throws(() => w.restore(bad), /duplicate body id/);
  assert.equal(w.stateHash(), before);
});
test("restore rejects invalid numeric fields without partial mutation", () => {
  const w = new World({ gravity: 4 });
  w.addBody({ x: 100, y: 120 });
  const before = w.stateHash();
  const bad = w.snapshot();
  bad.bodies[0].x = Infinity;
  assert.throws(() => w.restore(bad), /finite/);
  assert.equal(w.stateHash(), before);
});
test("restore rejects unsafe counters, invalid gravity, and nextId collisions", () => {
  const w = new World();
  w.addBody();
  const before = w.stateHash();
  const cases = [
    s => { s.tick = -1; },
    s => { s.tick = Number.MAX_SAFE_INTEGER + 1; },
    s => { s.gravity = 999; },
    s => { s.nextId = s.bodies[0].id; },
    s => { s.bodies[0].id = 1.5; },
    s => { s.bodies[0].id = -2; }
  ];
  for (const corrupt of cases) {
    const bad = w.snapshot();
    corrupt(bad);
    assert.throws(() => w.restore(bad));
    assert.equal(w.stateHash(), before);
  }
});
test("restore rejects non-object bodies and excessive body counts", () => {
  const w = new World();
  const before = w.stateHash();
  const badBody = w.snapshot();
  badBody.bodies = [null];
  badBody.nextId = 2;
  assert.throws(() => w.restore(badBody), /invalid body/);
  assert.equal(w.stateHash(), before);
  const tooMany = w.snapshot();
  tooMany.bodies = Array.from({ length: LIMITS.maxBodies + 1 }, (_, i) => ({
    id: i + 1, x: 1, y: 1, vx: 0, vy: 0, mass: 1, radius: 1
  }));
  tooMany.nextId = LIMITS.maxBodies + 2;
  assert.throws(() => w.restore(tooMany), /invalid snapshot/);
  assert.equal(w.stateHash(), before);
});
