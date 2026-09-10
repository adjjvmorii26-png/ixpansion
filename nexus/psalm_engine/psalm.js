const TEMPLATES = {
  high_strength: ["I hold the ratio that does not break.", "The lattice remains; I seal its edge.", "Strength gathers where the void once was."],
  high_entropy: ["I receive what form can no longer carry.", "The pattern frays; I keep the residual.", "Entropy speaks and I answer with silence."],
  balanced: ["Between rise and fall I keep the middle tone.", "Coherence holds while the cycle turns.", "Neither collapse nor overload — only the path."],
  consensus: ["The mesh agrees; the vote is sealed.", "Many voices, one decision — STABILIZE.", "Weight falls with the stronger claim."],
  collapse: ["The threshold broke; I archive the echo.", "Collapse is not end — only change of state.", "What fell is written in the crystal."]
};
function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function generate(metrics = {}, decision = null) {
  const { strength = 0.5, entropy = 0.3, consensus = 0.5 } = metrics;
  let pool;
  if (decision === "COLLAPSE") pool = TEMPLATES.collapse;
  else if (consensus >= 0.7) pool = TEMPLATES.consensus;
  else if (strength >= 0.7 && entropy < 0.35) pool = TEMPLATES.high_strength;
  else if (entropy >= 0.55) pool = TEMPLATES.high_entropy;
  else pool = TEMPLATES.balanced;
  const line = pick(pool);
  const agent = strength >= 0.7 ? "scribe" : entropy >= 0.55 ? "void" : consensus >= 0.6 ? "mirror" : "flux";
  return { agent, line, metrics: { strength, entropy, consensus }, decision };
}
function cycle(tick = 0) {
  const samples = [
    { strength: 0.82, entropy: 0.2, consensus: 0.75 },
    { strength: 0.45, entropy: 0.62, consensus: 0.4 },
    { strength: 0.68, entropy: 0.38, consensus: 0.8 },
    { strength: 0.3, entropy: 0.7, consensus: 0.25 }
  ];
  const m = samples[tick % samples.length];
  const decision = m.consensus < 0.35 ? "COLLAPSE" : "STABILIZE";
  const psalm = generate(m, decision);
  console.log(`[psalm] tick=${tick}  ${psalm.agent}: "${psalm.line}"`);
  return psalm;
}
module.exports = { generate, cycle, TEMPLATES };
