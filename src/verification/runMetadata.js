/**
 * Build a deterministic, serializable run metadata envelope.
 *
 * This is an evidence payload, not a signature or authenticity guarantee.
 * Integrators may pass the payload to the project's EvidenceEnvelope /
 * EvidenceVerifier implementation for source authorization, freshness,
 * HMAC/signature checks, and trust policy.
 */

function canonicalize(value) {
  if (value === null || typeof value === "string" || typeof value === "boolean") return value;
  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new TypeError("canonical data cannot contain non-finite numbers");
    return Object.is(value, -0) ? 0 : value;
  }
  if (Array.isArray(value)) return value.map(canonicalize);
  if (typeof value === "object") {
    const output = {};
    for (const key of Object.keys(value).sort()) {
      if (value[key] === undefined) throw new TypeError("canonical data cannot contain undefined values");
      output[key] = canonicalize(value[key]);
    }
    return output;
  }
  throw new TypeError("canonical data supports only JSON-compatible values");
}

export function canonicalJson(value) {
  return JSON.stringify(canonicalize(value));
}

export function createRunMetadata({
  runId,
  seed,
  config,
  engineVersion,
  commit = null,
  startedAt,
  endedAt = null,
  tickCount,
  eventSequence = 0,
  invariantFindings = [],
  finalState = null,
}) {
  if (typeof runId !== "string" || runId.trim() === "") throw new TypeError("runId is required");
  if (!Number.isInteger(seed) || seed < 0 || seed > 0xffffffff) throw new RangeError("seed must be uint32");
  if (typeof engineVersion !== "string" || engineVersion.trim() === "") throw new TypeError("engineVersion is required");
  if (!Number.isSafeInteger(tickCount) || tickCount < 0) throw new RangeError("tickCount must be a non-negative safe integer");
  if (!Number.isSafeInteger(eventSequence) || eventSequence < 0) throw new RangeError("eventSequence must be a non-negative safe integer");
  if (typeof startedAt !== "string" || Number.isNaN(Date.parse(startedAt))) throw new TypeError("startedAt must be a parseable timestamp");
  if (endedAt !== null && (typeof endedAt !== "string" || Number.isNaN(Date.parse(endedAt)))) {
    throw new TypeError("endedAt must be null or a parseable timestamp");
  }
  if (!config || typeof config !== "object" || Array.isArray(config)) throw new TypeError("config must be an object");
  if (!Array.isArray(invariantFindings)) throw new TypeError("invariantFindings must be an array");

  const payload = {
    schema: "ixpansion.simulation-evidence.v1",
    runId,
    seed: seed >>> 0,
    config: canonicalize(config),
    engineVersion,
    commit,
    startedAt: new Date(startedAt).toISOString(),
    endedAt: endedAt === null ? null : new Date(endedAt).toISOString(),
    tickCount,
    eventSequence,
    invariantFindings: canonicalize(invariantFindings),
    finalState: finalState === null ? null : canonicalize(finalState),
    assurance: {
      digest: "NOT_COMPUTED",
      authenticity: "UNVERIFIED",
      note: "Metadata is not proof of origin or correctness; verify with an authorized evidence verifier.",
    },
  };
  return payload;
}

/** SHA-256 canonical payload digest, using Web Crypto where available. */
export async function digestRunMetadata(metadata, subtle = globalThis.crypto?.subtle) {
  if (!subtle || typeof subtle.digest !== "function") {
    throw new Error("Web Crypto SHA-256 is unavailable; provide a compatible subtle crypto implementation");
  }
  const unsignedPayload = { ...metadata, assurance: { ...metadata.assurance, digest: "NOT_COMPUTED" } };
  const bytes = new TextEncoder().encode(canonicalJson(unsignedPayload));
  const digest = await subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
}
