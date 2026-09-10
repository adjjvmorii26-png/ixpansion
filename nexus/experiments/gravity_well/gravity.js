const { publish } = require("../../resonance_bus/bus.js");
function pull(nodes = [], G = 0.08) {
  const sorted = [...nodes].sort((a, b) => b.strength - a.strength);
  const well = sorted[0];
  if (!well) return { nodes, well: null, transfers: [] };
  const transfers = [];
  const out = nodes.map(n => ({ ...n }));
  out.forEach(n => {
    if (n.id === well.id) return;
    const gap = well.strength - n.strength;
    if (gap <= 0) return;
    const amount = Math.min(0.12, gap * G);
    n.coherence = Math.max(0.05, (n.coherence ?? 0.5) - amount);
    const w = out.find(x => x.id === well.id);
    w.coherence = Math.min(0.98, (w.coherence ?? 0.5) + amount * 0.8);
    transfers.push({ from: n.id, to: well.id, amount: +amount.toFixed(4) });
  });
  publish("GRAVITY", { well: well.id, n: transfers.length });
  return { nodes: out, well: well.id, transfers };
}
function cycle(tick = 0) {
  const nodes = [
    { id: "attention", strength: 0.74, entropy: 0.2, coherence: 0.7, consensus: 0.65 },
    { id: "quietus", strength: 0.4 + tick * 0.02, entropy: 0.5, coherence: 0.4, consensus: 0.35 },
    { id: "metamorph", strength: 0.66, entropy: 0.35, coherence: 0.6, consensus: 0.55 },
    { id: "void", strength: 0.35, entropy: 0.6, coherence: 0.3, consensus: 0.25 }
  ];
  const r = pull(nodes, 0.1);
  console.log(`[gravity] tick=${tick}  well=${r.well}  transfers=${r.transfers.length}`);
  r.transfers.forEach(t => console.log(`    ${t.from} → ${t.to}  Δ=${t.amount}`));
  return r;
}
module.exports = { pull, cycle };
if (require.main === module) { console.log("GRAVITY WELL…\n"); for (let t = 0; t < 3; t++) cycle(t); }
