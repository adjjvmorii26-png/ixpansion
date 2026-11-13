import test from "node:test";
import assert from "node:assert/strict";
import { mapBodyTo3D } from "./mapping.mjs";

test("maps centered body near origin with positive height", () => {
  const p = mapBodyTo3D({ x: 400, y: 80, radius: 14 });
  assert.ok(Math.abs(p.x) < 1e-9);
  assert.ok(p.y > 0);
  assert.equal(p.z, 0);
  assert.equal(p.r, 1);
});

test("respects explicit z and uses y as height", () => {
  const p = mapBodyTo3D({ x: 400, y: 3.5, z: 2, radius: 7 });
  assert.equal(p.z, 2);
  assert.equal(p.y, 3.5);
  assert.ok(p.r < 1);
});

test("clamps radius scale to minimum", () => {
  const p = mapBodyTo3D({ x: 0, y: 0, radius: 0.01 });
  assert.equal(p.r, 0.2);
});
