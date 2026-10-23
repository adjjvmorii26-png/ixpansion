import test from "node:test";
import assert from "node:assert/strict";
import { createRandom, FixedStepClock, createParticles, updateParticles, projectParticle } from "../apps/manifold_reactor/reactor-core.mjs";

test("seeded random sequences are reproducible and bounded", () => {
  const a = createRandom(1234), b = createRandom(1234);
  const left = Array.from({ length: 100 }, a), right = Array.from({ length: 100 }, b);
  assert.deepEqual(left, right);
  assert.ok(left.every((v) => v >= 0 && v < 1));
});
test("random rejects non-uint32 seeds", () => {
  assert.throws(() => createRandom(-1), RangeError);
  assert.throws(() => createRandom(1.5), RangeError);
  assert.throws(() => createRandom(0x100000000), RangeError);
});
test("fixed-step clock has no phantom first tick and bounds catch-up", () => {
  const clock = new FixedStepClock({ step: 1 / 60, maxFrameSeconds: 0.1, maxSteps: 2 });
  const ticks = [];
  clock.advance(1000, (_dt, tick) => ticks.push(tick));
  clock.advance(1100, (dt, tick) => { assert.ok(Math.abs(dt - 1 / 60) < 1e-12); ticks.push(tick); });
  assert.deepEqual(ticks, [0, 1]);
  assert.ok(clock.droppedSeconds > 0);
  assert.ok(clock.accumulator < clock.step);
});
test("clock rejects invalid timestamps and callbacks", () => {
  const clock = new FixedStepClock();
  assert.throws(() => clock.advance(NaN, () => {}), TypeError);
  assert.throws(() => clock.advance(1, null), TypeError);
});
test("particle population is deterministic and capped", () => {
  assert.deepEqual(createParticles({ count: 20, seed: 7 }), createParticles({ count: 20, seed: 7 }));
  assert.throws(() => createParticles({ count: 1201 }), RangeError);
  assert.throws(() => createParticles({ count: 0 }), RangeError);
});
test("all geometries keep particle coordinates finite", () => {
  for (const mode of ["torus", "sphere", "circuit", "mobius", "collapse"]) {
    const particles = createParticles({ count: 64, seed: 99 });
    updateParticles(particles, 1 / 60, mode, 1.5);
    for (const particle of particles) {
      const point = projectParticle(particle, mode, 1.4, 0.25);
      assert.ok(Number.isFinite(point.x) && Number.isFinite(point.y) && Number.isFinite(point.z));
    }
  }
});
test("updates reject negative or non-finite time and clamp energy", () => {
  const particles = createParticles({ count: 4 });
  assert.throws(() => updateParticles(particles, -1), RangeError);
  assert.throws(() => updateParticles(particles, NaN), RangeError);
  updateParticles(particles, 0.016, "torus", 100);
  assert.ok(particles.every((p) => Number.isFinite(p.angle)));
});
