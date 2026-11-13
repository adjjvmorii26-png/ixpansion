/**
 * World Canvas action engine v0.2.
 * Typed, allowlisted actions over Holodeck World with atomic validation and replay.
 * This is a deterministic toy-simulation control plane, not real-world actuation.
 */
const ACTIONS = new Set(["body.add", "body.impulse", "gravity.set", "world.step"]);
const finite = (value, name) => {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new TypeError(name + " must be a finite number");
  }
  return value;
};
const clone = value => JSON.parse(JSON.stringify(value));
const deepFreeze = value => {
  if (value && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value)) deepFreeze(child);
  }
  return value;
};

export class ActionEngine {
  constructor(world, { maxEvents = 2000 } = {}) {
    if (!world || typeof world.snapshot !== "function" ||
        typeof world.restore !== "function" || typeof world.stateHash !== "function") {
      throw new TypeError("world must implement snapshot, restore and stateHash");
    }
    if (!Number.isSafeInteger(maxEvents) || maxEvents < 1 || maxEvents > 100000) {
      throw new RangeError("maxEvents must be an integer from 1 to 100000");
    }
    this.world = world;
    this.maxEvents = maxEvents;
    this.events = [];
  }

  dispatch(action) {
    if (!action || typeof action !== "object" || Array.isArray(action)) {
      throw new TypeError("action must be an object");
    }
    if (!ACTIONS.has(action.type)) throw new RangeError("unsupported action type");
    const before = this.world.snapshot();
    const beforeHash = this.world.stateHash();
    try {
      this.#apply(action);
      const afterHash = this.world.stateHash();
      const event = deepFreeze({
        sequence: this.events.length + 1,
        type: action.type,
        payload: clone(action.payload ?? {}),
        beforeHash,
        afterHash,
        tick: this.world.tick
      });
      if (this.events.length >= this.maxEvents) {
        this.world.restore(before);
        throw new RangeError("event ledger capacity reached");
      }
      this.events.push(event);
      return event;
    } catch (error) {
      // Restore the complete snapshot on every rejected action.
      this.world.restore(before);
      throw error;
    }
  }

  #apply(action) {
    const p = action.payload ?? {};
    if (!p || typeof p !== "object" || Array.isArray(p)) {
      throw new TypeError("action payload must be an object");
    }
    switch (action.type) {
      case "body.add":
        this.world.addBody({
          x: p.x, y: p.y, vx: p.vx ?? 0, vy: p.vy ?? 0,
          mass: p.mass ?? 1, radius: p.radius ?? 14
        });
        break;
      case "body.impulse": {
        if (!Number.isSafeInteger(p.id) || p.id < 1) throw new TypeError("id must be a positive integer");
        const dx = finite(p.dx, "dx"), dy = finite(p.dy, "dy");
        if (Math.abs(dx) > 500 || Math.abs(dy) > 500) throw new RangeError("impulse exceeds action bounds");
        const body = this.world.bodies.find(item => item.id === p.id);
        if (!body) throw new RangeError("unknown body id");
        body.vx += dx / body.mass;
        body.vy += dy / body.mass;
        break;
      }
      case "gravity.set":
        this.world.setGravity(finite(p.value, "value"));
        break;
      case "world.step": {
        const count = p.count ?? 1;
        if (!Number.isSafeInteger(count) || count < 1 || count > 120) {
          throw new RangeError("step count must be an integer from 1 to 120");
        }
        const dt = p.dt ?? 1 / 120;
        finite(dt, "dt");
        if (dt <= 0 || dt > 1 / 30) throw new RangeError("dt must be in (0, 1/30]");
        for (let i = 0; i < count; i++) this.world.step(dt);
        break;
      }
    }
  }

  exportLedger() {
    return clone(this.events);
  }

  static replay(world, ledger) {
    if (!Array.isArray(ledger) || ledger.length > 100000) {
      throw new TypeError("ledger must be an array with at most 100000 events");
    }
    const engine = new ActionEngine(world, { maxEvents: Math.max(1, ledger.length) });
    for (let index = 0; index < ledger.length; index++) {
      const recorded = ledger[index];
      if (!recorded || typeof recorded !== "object" ||
          recorded.sequence !== index + 1 ||
          recorded.beforeHash !== world.stateHash()) {
        throw new Error("replay sequence or state diverged before event " + (recorded?.sequence ?? "?"));
      }
      const event = engine.dispatch({ type: recorded.type, payload: recorded.payload });
      if (event.afterHash !== recorded.afterHash || event.tick !== recorded.tick) {
        throw new Error("replay diverged after event " + recorded.sequence);
      }
    }
    return engine;
  }
}
