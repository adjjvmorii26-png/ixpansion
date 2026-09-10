const { publish } = require("../../resonance_bus/bus.js");
const { thresholds } = require("../../bridge/config.js");
function cascade(nodes = [], shock = 0.12) {
  const th = thresholds().collapse ?? 0.28;
  const collapsed = nodes.filter(n => (n.strength ?? 1) < th || (n.entropy ?? 0) > 0.75);
  if (!collapsed.length) return { nodes: nodes.map(n => ({ ...n })), collapsed: [], shocks: [] };
  const collapsedIds = new Set(collapsed.map(n => n.id));
  const shocks = [];
  const out = nodes.map(n => {
    if (collapsedIds.has(n.id)) return { ...n, strength: Math.max(0.05, n.strength * 0.5), entropy: Math.min(0.95, (n.entropy ?? 0.5) + 0.1) };
    const hit = Math.min(0.2, shock * collapsed.length * 0.5);
    shocks.push({ id: n.id, entropyDelta: hit });
    return { ...n, entropy: Math.min(0.95, (n.entropy ?? 0.3) + hit), coherence: Math.max(0.05, (n.coherence ?? 0.6) - hit * 0.5) };
  });
  publish("CASCADE", { collapsed: [...collapsedIds], shocks: shocks.length });
  return { nodes: out, collapsed: [...collapsedIds], shocks };
}
function cycle(tick = 0) {
  const nodes = [
    { id: "alpha", strength: 0.7, entropy: 0.25, coherence: 0.7 },
    { id: "beta", strength: 0.25 - tick * 0.05, entropy: 0.7 + tick * 0.05, coherence: 0.4 },
    { id: "delta", strength: 0.65, entropy: 0.3, coherence: 0.65 }
  ];
  const r = cascade(nodes, 0.1);
  console.log(`[cascade] tick=${tick}  collapsed=[${r.collapsed.join(",")}]  shocks=${r.shocks.length}`);
  return r;
}
module.exports = { cascade, cycle };
if (require.main === module) { console.log("CASCADE FAIL…\n"); for (let t = 0; t < 4; t++) cycle(t); }
