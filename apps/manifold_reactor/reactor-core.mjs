/** Framework-independent reactor simulation primitives. No DOM or ambient randomness. */
export function createRandom(seed = 0x5eed) {
  if (!Number.isInteger(seed) || seed < 0 || seed > 0xffffffff) throw new RangeError("seed must be an unsigned 32-bit integer");
  let state = seed >>> 0;
  return function random() {
    let t = (state += 0x6d2b79f5) >>> 0;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export class FixedStepClock {
  constructor({ step = 1 / 60, maxFrameSeconds = 0.1, maxSteps = 4 } = {}) {
    if (!Number.isFinite(step) || step <= 0) throw new RangeError("step must be positive");
    if (!Number.isFinite(maxFrameSeconds) || maxFrameSeconds <= 0) throw new RangeError("maxFrameSeconds must be positive");
    if (!Number.isSafeInteger(maxSteps) || maxSteps < 1) throw new RangeError("maxSteps must be a positive integer");
    this.step = step; this.maxFrameSeconds = maxFrameSeconds; this.maxSteps = maxSteps;
    this.accumulator = 0; this.tick = 0; this.droppedSeconds = 0; this.lastTimestamp = null;
  }
  reset() { this.accumulator = 0; this.lastTimestamp = null; }
  advance(timestampMs, update) {
    if (!Number.isFinite(timestampMs)) throw new TypeError("timestamp must be finite");
    if (typeof update !== "function") throw new TypeError("update must be a function");
    if (this.lastTimestamp === null) { this.lastTimestamp = timestampMs; return 0; }
    const elapsed = (timestampMs - this.lastTimestamp) / 1000;
    this.lastTimestamp = timestampMs;
    if (elapsed < 0) { this.accumulator = 0; return 0; }
    const accepted = Math.min(elapsed, this.maxFrameSeconds);
    this.droppedSeconds += elapsed - accepted; this.accumulator += accepted;
    let steps = 0;
    while (this.accumulator + Number.EPSILON >= this.step && steps < this.maxSteps) {
      update(this.step, this.tick); this.tick += 1; this.accumulator -= this.step;
      if (this.accumulator < 0 && this.accumulator > -1e-12) this.accumulator = 0;
      steps += 1;
    }
    if (this.accumulator >= this.step) {
      const discarded = Math.floor(this.accumulator / this.step) * this.step;
      this.accumulator -= discarded; this.droppedSeconds += discarded;
    }
    return this.accumulator / this.step;
  }
}

export function createParticles({ count = 180, seed = 0x5eed } = {}) {
  if (!Number.isSafeInteger(count) || count < 1 || count > 1200) throw new RangeError("count must be an integer between 1 and 1200");
  const random = createRandom(seed);
  return Array.from({ length: count }, (_, id) => ({
    id, angle: random() * Math.PI * 2, radius: 0.18 + random() * 0.78,
    height: (random() - 0.5) * 1.2, speed: (0.08 + random() * 0.3) * (random() < 0.5 ? -1 : 1),
    size: 1 + random() * 2,
  }));
}

export function updateParticles(particles, dt, mode = "torus", energy = 1) {
  if (!Number.isFinite(dt) || dt < 0) throw new RangeError("dt must be finite and non-negative");
  if (!Number.isFinite(energy)) throw new TypeError("energy must be finite");
  const speedScale = Math.max(0, Math.min(3, energy));
  for (const p of particles) {
    p.angle += dt * p.speed * speedScale;
    if (p.angle > Math.PI * 2) p.angle -= Math.PI * 2;
    if (p.angle < 0) p.angle += Math.PI * 2;
    if (mode === "sphere") p.radius = 0.55 + 0.1 * Math.sin(p.angle * 2 + p.id);
    else if (mode === "mobius") p.height = 0.45 * Math.sin(p.angle * 0.5 + p.id * 0.13);
    else if (mode === "collapse") p.radius = Math.max(0.04, p.radius - dt * 0.05);
    else if (mode === "circuit") p.radius = 0.65 + 0.12 * Math.sin(p.angle * 4);
  }
}

export function projectParticle(p, mode, aspect, time = 0) {
  const a = p.angle; let r = p.radius;
  let x = Math.cos(a) * r; let y = Math.sin(a) * r; let z = p.height;
  if (mode === "sphere") {
    const lat = p.height * Math.PI;
    x = Math.cos(a) * Math.cos(lat) * r; y = Math.sin(a) * Math.cos(lat) * r; z = Math.sin(lat) * r;
  } else if (mode === "mobius") {
    const half = a / 2;
    x = (r + p.height * Math.cos(half)) * Math.cos(a);
    y = (r + p.height * Math.cos(half)) * Math.sin(a); z = p.height * Math.sin(half);
  } else if (mode === "circuit") {
    x = Math.cos(a * 3) * r; y = Math.sin(a * 3) * r; z = Math.sin(a * 6) * 0.2;
  } else z += Math.sin(a * 2 + time) * 0.08;
  const perspective = 1 / Math.max(0.35, 1.5 + z * 0.25);
  return { x: x * perspective / Math.max(aspect, 0.25), y: y * perspective, z, scale: perspective };
}
