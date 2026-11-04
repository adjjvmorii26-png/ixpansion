import test from "node:test";
import assert from "node:assert/strict";
import { DeterministicRandom } from "../src/core/Random.js";
import { SimulationClock } from "../src/core/SimulationClock.js";
import { SpatialIndex } from "../src/spatial/SpatialIndex.js";
import { assertSimulationInvariants, inspectSimulationState } from "../src/verification/invariants.js";
import { canonicalJson, createRunMetadata } from "../src/verification/runMetadata.js";

test("seeded PRNG repeats the same sequence and snapshots restore it", () => {
  const a = new DeterministicRandom(42);
  const b = new DeterministicRandom(42);
  assert.deepEqual(Array.from({ length: 20 }, () => a.next()), Array.from({ length: 20 }, () => b.next()));
  const snapshot = a.snapshot();
  const expected = a.next();
  a.restore(snapshot);
  assert.equal(a.next(), expected);
});

test("PRNG rejects invalid seeds and ranges", () => {
  assert.throws(() => new DeterministicRandom(-1), RangeError);
  assert.throws(() => new DeterministicRandom(1.5), RangeError);
  const rng = new DeterministicRandom(7);
  assert.throws(() => rng.range(2, 1), RangeError);
  assert.throws(() => rng.int(1.2, 4), RangeError);
});

test("clock initializes without a phantom update and advances fixed ticks", () => {
  const clock = new SimulationClock({ targetFps: 60, maxSubSteps: 5 });
  const ticks = [];
  assert.equal(clock.tick(1000, (_dt, tick) => ticks.push(tick)), 0);
  clock.tick(1050, (dt, tick) => {
    assert.equal(dt, 1 / 60);
    ticks.push(tick);
  });
  assert.deepEqual(ticks, [0, 1, 2]);
  assert.equal(clock.tickCount, 3);
});

test("clock bounds catch-up and accounts for dropped time", () => {
  const clock = new SimulationClock({ targetFps: 60, maxSubSteps: 2, maxFrameTime: 0.25 });
  let updates = 0;
  clock.tick(0, () => updates++);
  clock.tick(1000, () => updates++);
  assert.equal(updates, 2);
  assert.ok(clock.droppedTimeSeconds > 0.7);
  assert.ok(clock.accumulator < clock.timestep);
  assert.equal(clock.overloadCount, 1);
});

test("clock ignores backwards time and validates callbacks", () => {
  const clock = new SimulationClock();
  clock.tick(100, () => {});
  assert.equal(clock.tick(90, () => { throw new Error("must not run"); }), 0);
  assert.throws(() => clock.tick(100, null), TypeError);
});

test("spatial index filters cell candidates by exact radius", () => {
  const index = new SpatialIndex({ cellSize: 10 });
  const near = { id: "near", position: { x: 1, y: 0, z: 0 } };
  const edge = { id: "edge", position: { x: 3, y: 0, z: 0 } };
  const far = { id: "far", position: { x: 9, y: 0, z: 0 } };
  index.rebuild([near, edge, far]);
  assert.deepEqual(index.getNearby({ x: 0, y: 0, z: 0 }, 3).map((e) => e.id).sort(), ["edge", "near"]);
  assert.deepEqual(index.getNearby({ x: 0, y: 0, z: 0 }, 0), []);
  assert.deepEqual(index.getNearby({ x: 1, y: 0, z: 0 }, 0, { exclude: near }), []);
});

test("spatial index validates positions and radius", () => {
  const index = new SpatialIndex();
  assert.throws(() => index.insert({ id: "bad", position: { x: NaN, y: 0, z: 0 } }), TypeError);
  assert.throws(() => index.getNearby({ x: 0, y: 0, z: 0 }, -1), RangeError);
});

test("simulation invariants catch duplicate IDs and non-finite vectors", () => {
  const state = {
    tick: 2,
    entities: [
      { id: "a", position: { x: 0, y: 0, z: 0 }, velocity: { x: 1, y: 0, z: 0 } },
      { id: "a", position: { x: Infinity, y: 0, z: 0 } },
    ],
  };
  const findings = inspectSimulationState(state);
  assert.ok(findings.some((f) => f.code === "ENTITY_ID_DUPLICATE"));
  assert.ok(findings.some((f) => f.code === "POSITION_INVALID"));
  assert.throws(() => assertSimulationInvariants(state), (error) => error.name === "SimulationInvariantError");
  assert.equal(assertSimulationInvariants({ tick: 0, entities: [] }), true);
});

test("run metadata is canonical and marks authenticity unverified", () => {
  const base = {
    runId: "run-1",
    seed: 12,
    config: { z: 2, a: 1 },
    engineVersion: "0.1.0",
    startedAt: "2026-10-18T00:00:00Z",
    tickCount: 5,
  };
  const metadata = createRunMetadata(base);
  assert.equal(metadata.schema, "ixpansion.simulation-evidence.v1");
  assert.equal(metadata.assurance.authenticity, "UNVERIFIED");
  assert.equal(canonicalJson({ b: 1, a: 2 }), canonicalJson({ a: 2, b: 1 }));
  assert.throws(() => createRunMetadata({ ...base, seed: -1 }), RangeError);
  assert.throws(() => canonicalJson({ value: undefined }), TypeError);
});
