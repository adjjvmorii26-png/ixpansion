function normalize(raw = {}) {
  const strength = clamp(raw.strength ?? raw.avg ?? raw.amplitude ?? raw.melt ?? raw.ingest ?? 0.5);
  const entropy = clamp(raw.entropy ?? raw.decay ?? raw.absence ?? (1 - strength) * 0.6);
  const coherence = clamp(raw.coherence ?? raw.resonance ?? strength * 0.9);
  const consensus = clamp(raw.consensus ?? raw.vote ?? coherence * 0.85);
  return { strength, entropy, coherence, consensus };
}
function clamp(n) { return Math.max(0, Math.min(1, +n || 0)); }
module.exports = { normalize, clamp };
