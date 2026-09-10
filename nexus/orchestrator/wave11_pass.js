const { diffract } = require("../experiment/entropy_diffraction/diffraction.js");
const { bond } = require("../experiment/coherence_lattice/lattice.js");
const { lock } = require("../experiment/phase_lock_choir/choir.js");
const { entry, balance } = require("../experiment/echo_ledger/ledger.js");
function fromNodes(nodes) {
  return (nodes || []).map(n => ({
    id: n.id || n.name || "sys", theme: n.theme || "unknown",
    strength: n.strength ?? 0.5, entropy: n.entropy ?? 0.3,
    coherence: n.coherence ?? 0.6, consensus: n.consensus ?? 0.5
  }));
}
function run(raw = []) {
  let nodes = fromNodes(raw);
  if (!nodes.length) {
    nodes = [
      { id: "attention", theme: "cognitive", strength: 0.74, entropy: 0.2, coherence: 0.7, consensus: 0.65 },
      { id: "chronovore", theme: "temporal", strength: 0.5, entropy: 0.7, coherence: 0.4, consensus: 0.4 },
      { id: "meridian", theme: "temporal", strength: 0.62, entropy: 0.35, coherence: 0.55, consensus: 0.6 },
      { id: "void", theme: "ontological", strength: 0.35, entropy: 0.6, coherence: 0.3, consensus: 0.3 }
    ];
  }
  console.log("▸ Wave 11 Pass");
  const d = diffract(nodes, 0.16);
  console.log(`  diffract beams=${d.beams.length}`);
  nodes = d.nodes;
  d.beams.forEach(b => entry(b.from, b.to, "entropy", b.amount, "diffract"));
  const lat = bond(nodes);
  console.log(`  lattice bonds=${lat.bonds.length}`);
  nodes = lat.nodes;
  const agents = nodes.map(n => ({ id: n.id, phase: (n.consensus ?? 0.5) * 0.7 + (n.coherence ?? 0.5) * 0.3, weight: n.strength }));
  const pl = lock(agents, 0.28);
  console.log(`  phase_lock locked=${pl.locked} spread=${pl.spread} boost=${pl.boost}`);
  if (pl.boost > 0) nodes = nodes.map(n => ({ ...n, consensus: Math.min(0.98, (n.consensus ?? 0.5) + pl.boost) }));
  const led = balance("entropy");
  console.log(`  ledger sum=${led.sum} entries=${led.entries}\n`);
  return { nodes, diffract: d, lattice: lat, phase_lock: pl, ledger: led };
}
module.exports = { run };
if (require.main === module) run();
