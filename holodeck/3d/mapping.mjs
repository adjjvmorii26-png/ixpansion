/** Pure 2D→3D mapping helpers (no Three.js). Testable without a browser. */
export function mapBodyTo3D(body, { originX = 400, originY = 400, scale = 40 } = {}) {
  const r = Math.max(0.2, (body.radius ?? 14) / 14);
  const x = ((body.x ?? 0) - originX) / scale;
  const z = typeof body.z === "number" ? body.z : 0;
  // Physics y increases downward in 2D canvas; invert for 3D up-axis when z not set
  const height = typeof body.z === "number"
    ? (body.y ?? r)
    : Math.max(r, (originY - (body.y ?? 0)) / scale);
  return { x, y: height, z, r };
}
