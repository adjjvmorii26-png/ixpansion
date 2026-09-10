const { publish } = require("../../resonance_bus/bus.js");
const FACES = [
  { name: "STABILIZE_WIND", bias: { consensus: 0.12, strength: 0.05 }, omen: "the die favors holding" },
  { name: "COLLAPSE_WIND", bias: { consensus: -0.15, entropy: 0.08 }, omen: "the die favors release" },
  { name: "ENTROPY_BLOOM", bias: { entropy: 0.12, coherence: -0.06 }, omen: "chaos is invited" },
  { name: "STRENGTH_GIFT", bias: { strength: 0.1, coherence: 0.05 }, omen: "a quiet gift of force" },
  { name: "NULL_FACE", bias: {}, omen: "the die shows nothing" },
  { name: "MIRROR_FACE", bias: {}, omen: "the die reflects the thrower" }
];
function cast() {
  const face = FACES[Math.floor(Math.random() * FACES.length)];
  publish("ORACLE_CAST", { face: face.name });
  return face;
}
function apply(metrics, face) {
  const m = { ...metrics };
  Object.entries(face.bias || {}).forEach(([k, v]) => { m[k] = Math.max(0, Math.min(1, (m[k] ?? 0.5) + v)); });
  return m;
}
function cycle(tick = 0) {
  const face = cast();
  const base = { strength: 0.65, entropy: 0.35, coherence: 0.6, consensus: 0.55 };
  const after = apply(base, face);
  console.log(`[oracle] tick=${tick}  ${face.name}  "${face.omen}"`);
  console.log(`    consensus ${base.consensus.toFixed(2)} → ${after.consensus.toFixed(2)}`);
  return { face, before: base, after };
}
module.exports = { FACES, cast, apply, cycle };
if (require.main === module) { console.log("ORACLE DIE…\n"); for (let t = 0; t < 5; t++) cycle(t); }
