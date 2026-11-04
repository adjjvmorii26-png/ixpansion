/**
 * Seeded Mulberry32 PRNG for reproducible simulation runs.
 *
 * Determinism contract: identical unsigned 32-bit seed + identical call order
 * produces the same sequence. This does not promise bit-identical physics
 * across engines or hardware.
 */
export class DeterministicRandom {
  constructor(seed = 1337) {
    if (!Number.isInteger(seed) || seed < 0 || seed > 0xffffffff) {
      throw new RangeError("seed must be an unsigned 32-bit integer");
    }
    this.initialSeed = seed >>> 0;
    this.state = this.initialSeed;
  }

  next() {
    let t = (this.state += 0x6d2b79f5) >>> 0;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }

  range(min, max) {
    if (!Number.isFinite(min) || !Number.isFinite(max) || max < min) {
      throw new RangeError("range requires finite bounds with max >= min");
    }
    return min + this.next() * (max - min);
  }

  int(min, max) {
    if (!Number.isSafeInteger(min) || !Number.isSafeInteger(max) || max < min) {
      throw new RangeError("int requires safe integer bounds with max >= min");
    }
    // The inclusive helper is intentionally limited to ranges where a
    // 32-bit uniform sample can be mapped without unsafe integer arithmetic.
    const span = max - min + 1;
    if (span > 0x100000000) {
      throw new RangeError("integer range may not exceed 2^32 values");
    }
    return min + Math.floor(this.next() * span);
  }

  sign() {
    return this.next() < 0.5 ? -1 : 1;
  }

  snapshot() {
    return { initialSeed: this.initialSeed, state: this.state >>> 0 };
  }

  restore(snapshot) {
    if (
      !snapshot ||
      !Number.isInteger(snapshot.initialSeed) ||
      snapshot.initialSeed < 0 ||
      snapshot.initialSeed > 0xffffffff ||
      !Number.isInteger(snapshot.state) ||
      snapshot.state < 0 ||
      snapshot.state > 0xffffffff
    ) {
      throw new TypeError("invalid PRNG snapshot");
    }
    this.initialSeed = snapshot.initialSeed >>> 0;
    this.state = snapshot.state >>> 0;
  }
}
