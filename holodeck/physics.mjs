/**
 * Holodeck Core v0.1 — deterministic, dependency-free toy physics.
 * This is a bounded 2D sandbox, not a validated engineering solver.
 */
export const LIMITS = Object.freeze({ gravity: [-30, 30], mass: [0.1, 1000], maxBodies: 128 });
const finite = (n, name) => {
  if (typeof n !== "number" || !Number.isFinite(n)) throw new TypeError(name + " must be finite");
  return n;
};
export class World {
  constructor({ gravity = 9.81, width = 800, height = 600 } = {}) {
    this.gravity = Math.max(LIMITS.gravity[0], Math.min(LIMITS.gravity[1], finite(gravity, "gravity")));
    this.width = Math.max(100, finite(width, "width"));
    this.height = Math.max(100, finite(height, "height"));
    this.tick = 0;
    this.bodies = [];
    this.nextId = 1;
  }
  addBody({ x = this.width / 2, y = 80, vx = 0, vy = 0, mass = 1, radius = 14 } = {}) {
    if (this.bodies.length >= LIMITS.maxBodies) throw new RangeError("body capacity reached");
    for (const [name, value] of Object.entries({ x, y, vx, vy, mass, radius })) finite(value, name);
    if (mass < LIMITS.mass[0] || mass > LIMITS.mass[1]) throw new RangeError("mass outside allowed range");
    if (radius <= 0 || radius > 100) throw new RangeError("radius outside allowed range");
    const body = { id: this.nextId++, x, y, vx, vy, mass, radius };
    this.bodies.push(body);
    return body.id;
  }
  setGravity(value) {
    finite(value, "gravity");
    if (value < LIMITS.gravity[0] || value > LIMITS.gravity[1]) throw new RangeError("gravity outside allowed range");
    this.gravity = value;
  }
  setMass(id, value) {
    finite(value, "mass");
    if (value < LIMITS.mass[0] || value > LIMITS.mass[1]) throw new RangeError("mass outside allowed range");
    const body = this.bodies.find(b => b.id === id);
    if (!body) throw new RangeError("unknown body id");
    body.mass = value;
  }
  step(dt = 1 / 120) {
    finite(dt, "dt");
    if (dt <= 0 || dt > 1 / 30) throw new RangeError("dt must be in (0, 1/30]");
    for (const b of this.bodies) {
      b.vy += this.gravity * dt;
      b.x += b.vx * dt;
      b.y += b.vy * dt;
      if (b.x < b.radius) { b.x = b.radius; b.vx = Math.abs(b.vx) * 0.82; }
      if (b.x > this.width - b.radius) { b.x = this.width - b.radius; b.vx = -Math.abs(b.vx) * 0.82; }
      if (b.y > this.height - b.radius) { b.y = this.height - b.radius; b.vy = -Math.abs(b.vy) * 0.72; if (Math.abs(b.vy) < 0.08) b.vy = 0; }
      if (b.y < b.radius) { b.y = b.radius; b.vy = Math.abs(b.vy) * 0.82; }
    }
    this.tick++;
  }
  snapshot() {
    return JSON.parse(JSON.stringify({ version: 1, gravity: this.gravity, width: this.width, height: this.height, tick: this.tick, nextId: this.nextId, bodies: this.bodies }));
  }
  restore(snapshot) {
    if (!snapshot || snapshot.version !== 1 || !Array.isArray(snapshot.bodies) || snapshot.bodies.length > LIMITS.maxBodies) throw new TypeError("invalid snapshot");
    const candidate = new World({ gravity: snapshot.gravity, width: snapshot.width, height: snapshot.height });
    candidate.tick = snapshot.tick;
    candidate.nextId = snapshot.nextId;
    for (const raw of snapshot.bodies) candidate.addBody(raw);
    candidate.tick = snapshot.tick;
    candidate.nextId = snapshot.nextId;
    Object.assign(this, candidate);
  }
  stateHash() {
    // Stable serialization + FNV-1a. Integrity checksum, not proof of correct physics.
    const text = JSON.stringify(this.snapshot());
    let hash = 0x811c9dc5;
    for (let i = 0; i < text.length; i++) { hash ^= text.charCodeAt(i); hash = Math.imul(hash, 0x01000193) >>> 0; }
    return hash.toString(16).padStart(8, "0");
  }
}
