import test from "node:test";
import assert from "node:assert/strict";
import { FrameLab } from "./frame-lab.mjs";

test("fixed-step simulation is independent of render cadence", () => {
  const fast = new FrameLab({ targetFPS: 0 });
  const slow = new FrameLab({ targetFPS: 0 });
  let a = 0, b = 0;
  fast.advance(0, () => a++);
  slow.advance(0, () => b++);
  for (let t = 10; t <= 1000; t += 10) fast.advance(t, () => a++);
  for (let t = 0; t <= 1000; t += 50) slow.advance(t, () => b++);
  assert.equal(a, b);
  assert.equal(fast.simulationSteps, slow.simulationSteps);
});

test("paused advance does not change simulation steps; single-step advances exactly once", () => {
  const lab = new FrameLab();
  let steps = 0;
  lab.advance(0, () => steps++);
  lab.advance(100, () => steps++, { paused: true });
  assert.equal(steps, 0);
  lab.singleStep(() => steps++);
  assert.equal(steps, 1);
  assert.equal(lab.simulationSteps, 1);
  assert.equal(lab.frameIndex, 3);
});

test("large frame gaps are bounded and reported as dropped time", () => {
  const lab = new FrameLab({ targetFPS: 0, maxFrameDelta: 0.1, maxSubSteps: 4 });
  let steps = 0;
  lab.advance(0, () => steps++);
  const metrics = lab.advance(1000, () => steps++);
  assert.ok(metrics.droppedSeconds > 0.8);
  assert.ok(metrics.stepsThisFrame <= 4);
});

test("target FPS rejects unsafe values and can be uncapped", () => {
  const lab = new FrameLab();
  assert.throws(() => lab.setTargetFPS(1000), /targetFPS/);
  lab.setTargetFPS(0);
  assert.equal(lab.targetFPS, 0);
});

test("capture, duplicate, and export preserve snapshots without aliasing", () => {
  const lab = new FrameLab({ maxCaptures: 3 });
  const state = { tick: 4, bodies: [{ id: 1, x: 10 }] };
  const first = lab.capture(state, { simTick: 4, stateHash: "abc", label: "initial" });
  state.bodies[0].x = 99;
  assert.equal(lab.getCapture(first.id).snapshot.bodies[0].x, 10);
  const copy = lab.duplicateCapture(first.id);
  assert.equal(copy.snapshot.bodies[0].x, 10);
  const exported = JSON.parse(lab.exportCaptures());
  assert.equal(exported.format, "ixpansion-holodeck-frames");
  assert.equal(exported.captures.length, 2);
});

test("capture storage is bounded and unknown duplicate ids fail", () => {
  const lab = new FrameLab({ maxCaptures: 2 });
  const one = lab.capture({ n: 1 });
  lab.capture({ n: 2 });
  lab.capture({ n: 3 });
  assert.equal(lab.captures.length, 2);
  assert.equal(lab.getCapture(one.id), null);
  assert.throws(() => lab.duplicateCapture(one.id), /unknown/);
});

test("render cadence is throttled independently from simulation stepping", () => {
  const lab = new FrameLab({ targetFPS: 30 });
  let steps = 0;
  const first = lab.advance(0, () => steps++);
  const early = lab.advance(10, () => steps++);
  const due = lab.advance(34, () => steps++);
  assert.equal(first.rendered, true);
  assert.equal(early.rendered, false);
  assert.equal(due.rendered, true);
  assert.ok(steps > 0);
});

test("frame image payloads are validated and preserved by duplication", () => {
  const lab = new FrameLab({ maxImageDataUrlLength: 2000 });
  const image = "data:image/jpeg;base64," + "A".repeat(32);
  const first = lab.capture({ tick: 1 }, { imageDataUrl: image });
  const duplicate = lab.duplicateCapture(first.id);
  assert.equal(duplicate.imageDataUrl, image);
  assert.throws(() => lab.capture({}, { imageDataUrl: "javascript:alert(1)" }), /bounded/);
  assert.throws(() => lab.capture({}, { imageDataUrl: "data:image/png;base64," + "A".repeat(3000) }), /bounded/);
});
