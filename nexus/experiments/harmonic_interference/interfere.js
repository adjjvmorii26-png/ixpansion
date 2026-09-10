const { publish } = require("../../resonance_bus/bus.js");
function interfere(nodes = [], sources = []) {
  const out = nodes.map(n => ({ ...n }));
  const field = [];
  out.forEach(n => {
    let sum = 0;
    sources.forEach(src => {
      if (src.id === n.id) return;
      const d = Math.abs((src.phase ?? 0) - (n.phase ?? (n.consensus ?? 0.5)));
      const aligned = 1 - Math.min(1, d * 2);
      sum += (aligned * 2 - 1) * (src.amplitude ?? 0.1);
    });
    const before = n.coherence ?? 0.5;
    n.coherence = Math.max(0.05, Math.min(0.98, before + sum));
    field.push({ id: n.id, delta: +(n.coherence - before).toFixed(4), coherence: n.coherence });
  });
  const constructive = field.filter(f => f.delta > 0).length;
  const destructive = field.filter(f => f.delta < 0).length;
  publish("INTERFERE", { constructive, destructive });
  return { nodes: out, field, constructive, destructive };
}
function cycle(tick = 0) {
  const nodes = [
    { id: "a", phase: 0.1, consensus: 0.1, coherence: 0.5, strength: 0.7 },
    { id: "b", phase: 0.12 + tick * 0.05, consensus: 0.15, coherence: 0.5, strength: 0.65 },
    { id: "c", phase: 0.7, consensus: 0.7, coherence: 0.55, strength: 0.6 },
    { id: "d", phase: 0.72, consensus: 0.75, coherence: 0.5, strength: 0.58 }
  ];
  const sources = [
    { id: "a", phase: nodes[0].phase, amplitude: 0.08 },
    { id: "c", phase: nodes[2].phase, amplitude: 0.08 }
  ];
  const r = interfere(nodes, sources);
  console.log(`[interfere] tick=${tick}  +${r.constructive} / -${r.destructive}`);
  r.field.forEach(f => console.log(`    ${f.id} Δ=${f.delta} coh=${f.coherence.toFixed(3)}`));
  return r;
}
module.exports = { interfere, cycle };
if (require.main === module) { console.log("HARMONIC INTERFERENCE…\n"); for (let t = 0; t < 4; t++) cycle(t); }
