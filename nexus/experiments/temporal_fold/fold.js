const { publish } = require("../../resonance_bus/bus.js");
const past = new Map();
function remember(id, metrics) { past.set(id, { ...metrics, _t: Date.now() }); }
function fold(nodes = [], alpha = 0.5) {
  const out = nodes.map(n => {
    const p = past.get(n.id);
    if (!p) { remember(n.id, n); return { ...n, folded: false }; }
    const blend = (k) => +((p[k] ?? 0.5) * (1 - alpha) + (n[k] ?? 0.5) * alpha).toFixed(4);
    return { ...n, strength: blend("strength"), entropy: blend("entropy"), coherence: blend("coherence"), consensus: blend("consensus"), folded: true, alpha };
  });
  out.forEach(n => remember(n.id, n));
  publish("TEMPORAL_FOLD", { alpha, n: out.filter(x => x.folded).length });
  return { nodes: out, alpha };
}
function cycle(tick = 0) {
  const nodes = [
    { id: "chrono", strength: 0.8 - tick * 0.1, entropy: 0.2 + tick * 0.08, coherence: 0.7, consensus: 0.65 },
    { id: "still", strength: 0.55, entropy: 0.35, coherence: 0.5, consensus: 0.5 }
  ];
  if (tick === 0) { nodes.forEach(n => remember(n.id, n)); console.log(`[fold] tick=0  remembered past`); }
  const alpha = tick === 0 ? 1 : 0.35 + tick * 0.1;
  const r = fold(nodes, Math.min(1, alpha));
  console.log(`[fold] tick=${tick}  alpha=${r.alpha}`);
  r.nodes.forEach(n => console.log(`    ${n.id} str=${n.strength} ent=${n.entropy} folded=${n.folded}`));
  return r;
}
module.exports = { remember, fold, cycle, past };
if (require.main === module) { console.log("TEMPORAL FOLD…\n"); past.clear(); for (let t = 0; t < 4; t++) cycle(t); }
