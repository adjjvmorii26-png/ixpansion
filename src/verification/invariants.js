/**
 * Pure invariant checks for a simulation state.
 * State contract: { tick, entities: [{ id, position: {x,y,z}, ... }] }.
 * Returns findings; it never mutates state or treats findings as proof of
 * authenticity. Callers decide whether a finding should halt a run.
 */
export function inspectSimulationState(state, { maxEntities = 1000000 } = {}) {
  const findings = [];
  const add = (code, path, message) => findings.push({ code, path, message });

  if (!state || typeof state !== "object" || Array.isArray(state)) {
    return [{ code: "STATE_INVALID", path: "$", message: "state must be an object" }];
  }
  if (!Number.isSafeInteger(state.tick) || state.tick < 0) {
    add("TICK_INVALID", "$.tick", "tick must be a non-negative safe integer");
  }
  if (!Array.isArray(state.entities)) {
    add("ENTITIES_INVALID", "$.entities", "entities must be an array");
    return findings;
  }
  if (state.entities.length > maxEntities) {
    add("ENTITY_LIMIT_EXCEEDED", "$.entities", "entity count exceeds configured limit");
  }

  const ids = new Set();
  for (let i = 0; i < state.entities.length; i++) {
    const entity = state.entities[i];
    const path = "$.entities[" + i + "]";
    if (!entity || typeof entity !== "object" || Array.isArray(entity)) {
      add("ENTITY_INVALID", path, "entity must be an object");
      continue;
    }
    if (typeof entity.id !== "string" && !(Number.isSafeInteger(entity.id) && entity.id >= 0)) {
      add("ENTITY_ID_INVALID", path + ".id", "id must be a string or non-negative safe integer");
    } else {
      const key = typeof entity.id + ":" + String(entity.id);
      if (ids.has(key)) add("ENTITY_ID_DUPLICATE", path + ".id", "entity id must be unique");
      ids.add(key);
    }
    const p = entity.position;
    if (!p || !Number.isFinite(p.x) || !Number.isFinite(p.y) || !Number.isFinite(p.z)) {
      add("POSITION_INVALID", path + ".position", "position must contain finite x, y, z");
    }
    if (entity.velocity !== undefined) {
      const v = entity.velocity;
      if (!v || !Number.isFinite(v.x) || !Number.isFinite(v.y) || !Number.isFinite(v.z)) {
        add("VELOCITY_INVALID", path + ".velocity", "velocity must contain finite x, y, z");
      }
    }
  }
  return findings;
}

export function assertSimulationInvariants(state, options) {
  const findings = inspectSimulationState(state, options);
  if (findings.length) {
    const error = new Error("Simulation invariant violation: " + findings.map((f) => f.code).join(", "));
    error.name = "SimulationInvariantError";
    error.findings = findings;
    throw error;
  }
  return true;
}
