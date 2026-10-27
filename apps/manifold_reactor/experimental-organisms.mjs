/**
 * Deterministic, framework-independent experimental organism primitives.
 *
 * These objects produce simulation state only. They do not access the DOM,
 * renderer, audio devices, network, or external resource systems.
 */

function finiteNumber(value, name) {
  if (!Number.isFinite(value)) throw new TypeError(`${name} must be finite`);
}

/**
 * Emits cached temporal echoes when a crystal's remaining amplitude falls
 * below minResidual. Cache entries are bounded and expire by simulation epoch.
 */
export class TemporalEchoRule {
  constructor({
    decayRate = 0.0142,
    minResidual = 0.15,
    maxCacheEntries = 1024,
    cacheTtlEpochs = 600,
  } = {}) {
    finiteNumber(decayRate, "decayRate");
    finiteNumber(minResidual, "minResidual");
    if (decayRate <= 0) throw new RangeError("decayRate must be positive");
    if (minResidual <= 0 || minResidual >= 1) {
      throw new RangeError("minResidual must be between 0 and 1");
    }
    if (!Number.isSafeInteger(maxCacheEntries) || maxCacheEntries < 1) {
      throw new RangeError("maxCacheEntries must be a positive integer");
    }
    if (!Number.isSafeInteger(cacheTtlEpochs) || cacheTtlEpochs < 1) {
      throw new RangeError("cacheTtlEpochs must be a positive integer");
    }
    this.decayRate = decayRate;
    this.minResidual = minResidual;
    this.maxCacheEntries = maxCacheEntries;
    this.cacheTtlEpochs = cacheTtlEpochs;
    this.phantomCache = new Map();
  }

  evaluate(crystalState, currentEpoch) {
    if (!crystalState || typeof crystalState !== "object") {
      throw new TypeError("crystalState must be an object");
    }
    if (typeof crystalState.id !== "string" || crystalState.id.length === 0) {
      throw new TypeError("crystalState.id must be a non-empty string");
    }
    finiteNumber(crystalState.birthEpoch, "birthEpoch");
    finiteNumber(currentEpoch, "currentEpoch");
    if (currentEpoch < crystalState.birthEpoch) {
      throw new RangeError("currentEpoch cannot precede birthEpoch");
    }
    if (!Array.isArray(crystalState.vector) ||
        !Number.isFinite(crystalState.vector[0]) ||
        !Number.isFinite(crystalState.vector[1])) {
      throw new TypeError("crystalState.vector must contain two finite coordinates");
    }

    this.prune(currentEpoch);
    const age = currentEpoch - crystalState.birthEpoch;
    const residual = Math.exp(-this.decayRate * age);
    if (residual >= this.minResidual) return null;
    return this.condenseEcho(crystalState, residual, currentEpoch);
  }

  condenseEcho(crystal, residual, currentEpoch) {
    // Epoch bucket keeps identity stable across repeated evaluations in the
    // same simulation epoch, while avoiding per-frame key churn.
    const phantomKey = `echo:${crystal.id}:${Math.floor(currentEpoch)}`;
    const cached = this.phantomCache.get(phantomKey);
    if (cached) {
      this.phantomCache.delete(phantomKey);
      this.phantomCache.set(phantomKey, cached);
      return cached;
    }

    const phantomState = Object.freeze({
      id: phantomKey,
      originId: crystal.id,
      phaseShift: Math.atan2(crystal.vector[1], crystal.vector[0]),
      amplitude: 1 - residual,
      createdEpoch: currentEpoch,
      expiresEpoch: currentEpoch + this.cacheTtlEpochs,
      active: true,
    });

    this.phantomCache.set(phantomKey, phantomState);
    while (this.phantomCache.size > this.maxCacheEntries) {
      this.phantomCache.delete(this.phantomCache.keys().next().value);
    }
    return phantomState;
  }

  prune(currentEpoch) {
    finiteNumber(currentEpoch, "currentEpoch");
    for (const [key, echo] of this.phantomCache) {
      if (echo.expiresEpoch < currentEpoch) this.phantomCache.delete(key);
    }
  }

  clear() {
    this.phantomCache.clear();
  }
}

/**
 * A bounded adversary action generator. It requests a drain; it never mutates
 * the world's bandwidth itself. The host simulation must validate and apply it.
 */
export class VacuumLeech {
  constructor({
    id,
    initialBandwidthLoad = 0,
    siphonRate = 0.042,
    activationThreshold = 800,
    maxDrainPerTick = 50,
    hostGate = "SOL-3-GATE",
  }) {
    if (typeof id !== "string" || id.length === 0) {
      throw new TypeError("id must be a non-empty string");
    }
    for (const [name, value] of Object.entries({
      initialBandwidthLoad, siphonRate, activationThreshold, maxDrainPerTick,
    })) finiteNumber(value, name);
    if (initialBandwidthLoad < 0 || siphonRate < 0 ||
        activationThreshold < 0 || maxDrainPerTick < 0) {
      throw new RangeError("loads, rates, thresholds, and caps must be non-negative");
    }
    if (typeof hostGate !== "string" || hostGate.length === 0) {
      throw new TypeError("hostGate must be a non-empty string");
    }
    this.id = id;
    this.initialBandwidthLoad = initialBandwidthLoad;
    this.siphonRate = siphonRate;
    this.activationThreshold = activationThreshold;
    this.maxDrainPerTick = maxDrainPerTick;
    this.hostGate = hostGate;
    this.attached = true;
  }

  perception(worldState) {
    if (!worldState || typeof worldState !== "object") {
      throw new TypeError("worldState must be an object");
    }
    const load = worldState.subspaceBandwidth ?? this.initialBandwidthLoad;
    finiteNumber(load, "subspaceBandwidth");
    if (load < 0) throw new RangeError("subspaceBandwidth must be non-negative");
    return load;
  }

  action(bandwidth) {
    finiteNumber(bandwidth, "bandwidth");
    if (bandwidth < 0) throw new RangeError("bandwidth must be non-negative");
    if (!this.attached || bandwidth <= this.activationThreshold) {
      return Object.freeze({ type: "DORMANT", agentId: this.id });
    }
    const drain = Math.min(this.siphonRate * bandwidth, this.maxDrainPerTick, bandwidth);
    return Object.freeze({
      type: "SIPHON_ENERGY",
      agentId: this.id,
      drain,
      target: this.hostGate,
    });
  }

  neutralize() {
    this.attached = false;
    this.siphonRate = 0;
    return Object.freeze({
      type: "NEUTRALIZED",
      agentId: this.id,
      message: `Leech ${this.id} neutralized by Sentinel pulse-countermeasure.`,
    });
  }
}
