const { publish } = require("../../resonance_bus/bus.js");
function bond(nodes = [], maxGap = 0.15) {
  const bonds = [];
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      const gap = Math.abs(a.strength - b.strength);
      const align = 1 - Math.abs((a.consensus ?? 0.5) - (b.consensus ?? 0.5));
      if (gap <= maxGap && align > 0.7) bonds.push({ a: a.id, b: b.id, gap: +gap.toFixed(3), align: +align.toFixed(3) });
    }
  }
  const out = nodes.map(n => ({ ...n }));
  bonds.forEach(bond => {
    const A = out.find(n => n.id === bond.a), B = out.find(n => n.id === bond.b);
    if (!A || !B) return;
    const avg = ((A.coherence ?? 0.5) + (B.coherence ?? 0.5)) / 2;
    const lift = 0.04 * bond.align;
    A.coherence = Math.min(0.98, avg + lift);
    B.coherence = Math.min(0.98, avg + lift);
  });
  publish("LATTICE", { bonds: bonds.length });
  return { nodes: out, bonds };
}
function cycle(tick = 0) {
  const nodes = [
    { id: "scribe", strength: 0.72, coherence: 0.55, consensus: 0.7 },
    { id: "mirror", strength: 0.70 + tick * 0.01, coherence: 0.5, consensus: 0.68 },
    { id: "void", strength: 0.4, coherence: 0.3, consensus: 0.3 },
    { id: "flux", strength: 0.71, coherence: 0.52, consensus: 0.65 }
  ];
  const r = bond(nodes);
  console.log(`[lattice] tick=${tick}  bonds=${r.bonds.length}`);
  r.bonds.forEach(b => console.log(`    ${b.a}↔${b.b}  gap=${b.gap} align=${b.align}`));
  return r;
}
module.exports = { bond, cycle };
if (require.main === module) { console.log("COHERENCE LATTICE…\n"); for (let t = 0; t < 3; t++) cycle(t); }
