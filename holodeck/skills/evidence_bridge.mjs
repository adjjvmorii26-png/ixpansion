/** Creates provenance envelopes; status labels are assertions, not cryptographic verification. */
export function createSkillEvidence({ skill, result, context = {}, now = () => Date.now() }) {
  if (!skill || !result || typeof result.status !== "string") throw new TypeError("skill and result required");
  return Object.freeze({
    schema: "ixpansion.skill-evidence.v0.1",
    eventId: `skill-event-${now()}`,
    skill: { id: skill.id, version: skill.version },
    execution: { status: result.status, reason: result.reason ?? null },
    source: { mode: context.mode ?? "SIMULATED", evidenceStatus: "PENDING" },
    output: result.status === "COMPLETED" ? structuredClone(result.output) : null,
    createdAt: new Date(now()).toISOString()
  });
}
