const { pull } = require("../experiment/gravity_well/gravity.js");
const { cascade } = require("../experiment/cascade_fail/cascade.js");
const { swarm } = require("../experiment/faction_swarm/swarm.js");
const { bookmark, restore, list } = require("../experiment/chrono_bookmark/bookmark.js");
function fromExec(results = []) {
  return (results || []).map(r => ({
    id: (r.name || "sys").split("-")[0], name: r.name,
    strength: r.metrics?.strength ?? 0.5, entropy: r.metrics?.entropy ?? 0.3,
    coherence: r.metrics?.coherence ?? 0.6, consensus: r.metrics?.consensus ?? 0.5, theme: r.theme
  }));
}
function themeFactions(nodes) {
  const factions = {};
  nodes.forEach(n => { const t = n.theme || "unknown"; if (!factions[t]) factions[t] = []; factions[t].push(n.id); });
  return factions;
}
function run(execResults = [], opts = {}) {
  let nodes = fromExec(execResults);
  if (!nodes.length) return { nodes: [], gravity: null, cascade: null, swarm: null, bookmark: null };
  const snapName = opts.bookmarkName || "cycle_start";
  bookmark(snapName, {
    strength: nodes.reduce((s, n) => s + n.strength, 0) / nodes.length,
    entropy: nodes.reduce((s, n) => s + n.entropy, 0) / nodes.length,
    coherence: nodes.reduce((s, n) => s + n.coherence, 0) / nodes.length,
    consensus: nodes.reduce((s, n) => s + n.consensus, 0) / nodes.length
  });
  console.log("▸ Wave 9 Pass");
  const g = pull(nodes, 0.09);
  console.log(`  gravity well=${g.well} transfers=${g.transfers.length}`);
  nodes = g.nodes;
  const c = cascade(nodes, 0.1);
  console.log(`  cascade collapsed=[${c.collapsed.join(",") || "none"}] shocks=${c.shocks.length}`);
  nodes = c.nodes;
  const s = swarm(nodes, themeFactions(nodes));
  console.log(`  swarm ${s.decision} consensus=${s.consensus} factions=${Object.keys(s.factionScore).length}`);
  let restored = null;
  if (s.decision === "COLLAPSE" && s.consensus < 0.35 && opts.autoRestore) {
    restored = restore(snapName);
    console.log(`  chrono restore "${snapName}"`);
  }
  console.log();
  return { nodes, gravity: { well: g.well, transfers: g.transfers.length }, cascade: { collapsed: c.collapsed, shocks: c.shocks.length }, swarm: { decision: s.decision, consensus: s.consensus }, bookmark: { name: snapName, slots: list(), restored: !!restored } };
}
module.exports = { run, fromExec, themeFactions };
if (require.main === module) {
  run([
    { name: "attention-labyrinth", metrics: { strength: 0.74, entropy: 0.15, coherence: 0.7, consensus: 0.65 }, theme: "cognitive" },
    { name: "quietus-array", metrics: { strength: 0.35, entropy: 0.62, coherence: 0.4, consensus: 0.3 }, theme: "ontological" },
    { name: "metamorph-forge", metrics: { strength: 0.66, entropy: 0.35, coherence: 0.6, consensus: 0.55 }, theme: "transformative" },
    { name: "chronovore-archive", metrics: { strength: 0.2, entropy: 0.8, coherence: 0.3, consensus: 0.25 }, theme: "temporal" }
  ], { autoRestore: true });
}
