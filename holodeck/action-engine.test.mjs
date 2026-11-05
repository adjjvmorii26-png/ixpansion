import test from "node:test";
import assert from "node:assert/strict";
import { World } from "./physics.mjs";
import { ActionEngine } from "./action-engine.mjs";

test("typed actions mutate world and append hash-linked events", () => {
  const world = new World({ gravity: 0, width: 400, height: 300 });
  const engine = new ActionEngine(world);
  const add = engine.dispatch({ type: "body.add", payload: { x: 100, y: 80, mass: 2 } });
  assert.equal(add.sequence, 1);
  assert.equal(add.beforeHash.length, 8);
  assert.equal(world.bodies.length, 1);
  engine.dispatch({ type: "body.impulse", payload: { id: 1, dx: 10, dy: -4 } });
  assert.equal(world.bodies[0].vx, 5);
  assert.equal(world.bodies[0].vy, -2);
});

test("rejected actions leave world and ledger unchanged", () => {
  const world = new World();
  const engine = new ActionEngine(world);
  const before = world.stateHash();
  assert.throws(() => engine.dispatch({ type: "body.impulse", payload: { id: 99, dx: 1, dy: 1 } }), /unknown body/);
  assert.throws(() => engine.dispatch({ type: "gravity.set", payload: { value: 999 } }), /gravity/);
  assert.throws(() => engine.dispatch({ type: "world.step", payload: { count: 121 } }), /step count/);
  assert.throws(() => engine.dispatch({ type: "shell.exec", payload: { command: "unsafe" } }), /unsupported/);
  assert.equal(world.stateHash(), before);
  assert.equal(engine.exportLedger().length, 0);
});

test("bounded action payloads and ledger capacity fail closed", () => {
  const world = new World();
  const engine = new ActionEngine(world, { maxEvents: 1 });
  engine.dispatch({ type: "body.add", payload: { x: 20, y: 20 } });
  const before = world.stateHash();
  assert.throws(() => engine.dispatch({ type: "world.step", payload: { count: 1 } }), /ledger capacity/);
  assert.equal(world.stateHash(), before);
  assert.throws(() => engine.dispatch({ type: "body.impulse", payload: { id: 1, dx: 501, dy: 0 } }), /bounds/);
});

test("event ledger deterministically replays from identical initial state", () => {
  const initial = new World({ gravity: 3, width: 500, height: 400 }).snapshot();
  const firstWorld = new World(); firstWorld.restore(initial);
  const first = new ActionEngine(firstWorld);
  first.dispatch({ type: "body.add", payload: { x: 150, y: 40, vx: 2, mass: 3 } });
  first.dispatch({ type: "body.impulse", payload: { id: 1, dx: 12, dy: -6 } });
  first.dispatch({ type: "world.step", payload: { count: 30, dt: 1 / 120 } });
  const replayWorld = new World(); replayWorld.restore(initial);
  ActionEngine.replay(replayWorld, first.exportLedger());
  assert.equal(replayWorld.stateHash(), firstWorld.stateHash());
});

test("replay detects tampered or out-of-order event history", () => {
  const w = new World();
  const e = new ActionEngine(w);
  e.dispatch({ type: "body.add", payload: { x: 30, y: 30 } });
  const ledger = e.exportLedger();
  ledger[0].afterHash = "deadbeef";
  assert.throws(() => ActionEngine.replay(new World(), ledger), /diverged after event/);
});


test("world.step enforces the physics time-step interval before mutation", () => {
  const world = new World();
  const engine = new ActionEngine(world);
  const before = world.stateHash();
  for (const dt of [0, -0.001, 1 / 29, NaN, Infinity]) {
    assert.throws(() => engine.dispatch({ type: "world.step", payload: { count: 1, dt } }));
    assert.equal(world.stateHash(), before);
    assert.equal(engine.exportLedger().length, 0);
  }
});

test("returned event payloads are deeply immutable and detached from input", () => {
  const world = new World();
  const engine = new ActionEngine(world);
  const payload = { x: 20, y: 30, metadata: { label: "original" } };
  const event = engine.dispatch({ type: "body.add", payload });
  payload.metadata.label = "mutated input";
  assert.equal(event.payload.metadata.label, "original");
  assert.equal(Object.isFrozen(event.payload), true);
  assert.equal(Object.isFrozen(event.payload.metadata), true);
  assert.throws(() => { event.payload.metadata.label = "tampered"; }, TypeError);
  assert.equal(engine.exportLedger()[0].payload.metadata.label, "original");
});

test("replay rejects discontinuous event sequence numbers", () => {
  const world = new World();
  const engine = new ActionEngine(world);
  engine.dispatch({ type: "body.add", payload: { x: 20, y: 20 } });
  engine.dispatch({ type: "world.step", payload: { count: 1 } });
  const ledger = engine.exportLedger();
  ledger[1].sequence = 3;
  assert.throws(() => ActionEngine.replay(new World(), ledger), /sequence or state diverged/);
});
