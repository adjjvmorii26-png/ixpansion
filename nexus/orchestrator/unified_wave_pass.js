const wave9 = require("./wave9_pass.js");
const wave11 = require("./wave11_pass.js");
const wave12 = require("./wave12_pass.js");
function fromExec(results = []) {
  return (results || []).map(r => ({
    id: (r.name || "sys").split("-")[0], name: r.name, theme: r.theme || "unknown",
    strength: r.metrics?.strength ?? 0.5, entropy: r.metrics?.entropy ?? 0.3,
    coherence: r.metrics?.coherence ?? 0.6, consensus: r.metrics?.consensus ?? 0.5,
    phase: r.metrics?.consensus ?? 0.5
  }));
}
function run(execResults = [], opts = {}) {
  console.log("▸ Unified Wave Pass (9 → 11 → 12)");
  const nodes0 = fromExec(execResults);
  const w9 = wave9.run(execResults, { autoRestore: opts.autoRestore !== false });
  const nodesAfter9 = (w9.nodes && w9.nodes.length) ? w9.nodes : nodes0;
  const w11 = wave11.run(nodesAfter9.map(n => ({
    id: n.id, theme: n.theme || "unknown", strength: n.strength, entropy: n.entropy,
    coherence: n.coherence, consensus: n.consensus
  })));
  const nodesAfter11 = (w11.nodes && w11.nodes.length) ? w11.nodes : nodesAfter9;
  const w12 = wave12.run(nodesAfter11.map(n => ({ ...n, phase: n.consensus ?? 0.5 })));
  const summary = {
    wave9: { gravity: w9.gravity, cascade: w9.cascade, swarm: w9.swarm?.decision, consensus: w9.swarm?.consensus },
    wave11: { beams: w11.diffract?.beams?.length, bonds: w11.lattice?.bonds?.length, locked: w11.phase_lock?.locked, boost: w11.phase_lock?.boost },
    wave12: { fog: w12.fog?.decision, fogConsensus: w12.fog?.consensus, fogged: w12.fog?.fogged }
  };
  console.log("  summary:", JSON.stringify(summary));
  console.log();
  return { w9, w11, w12, summary, nodes: w12.nodes || nodesAfter11 };
}
module.exports = { run, fromExec };
if (require.main === module) {
  run([
    { name: "attention-labyrinth", metrics: { strength: 0.74, entropy: 0.2, coherence: 0.7, consensus: 0.65 }, theme: "cognitive" },
    { name: "chronovore-archive", metrics: { strength: 0.45, entropy: 0.7, coherence: 0.4, consensus: 0.4 }, theme: "temporal" },
    { name: "quietus-array", metrics: { strength: 0.35, entropy: 0.55, coherence: 0.35, consensus: 0.35 }, theme: "ontological" },
    { name: "metamorph-forge", metrics: { strength: 0.66, entropy: 0.35, coherence: 0.6, consensus: 0.55 }, theme: "transformative" }
  ]);
}
