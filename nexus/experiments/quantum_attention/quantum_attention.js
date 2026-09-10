const { publish } = require("../../resonance_bus/bus.js");
function superpose(signals = []) {
  const total = signals.reduce((s, x) => s + (x.amplitude || 0), 0) || 1;
  return signals.map(s => ({ ...s, probability: (s.amplitude || 0) / total, collapsed: false }));
}
function observe(superposed, preferId = null) {
  let chosen;
  if (preferId) chosen = superposed.find(s => s.id === preferId) || superposed[0];
  else {
    const r = Math.random(); let acc = 0;
    for (const s of superposed) { acc += s.probability; if (r <= acc) { chosen = s; break; } }
    chosen = chosen || superposed[superposed.length - 1];
  }
  const result = superposed.map(s => ({
    ...s, collapsed: s.id === chosen.id,
    postEntropy: s.id === chosen.id ? 0.15 : 0.45 + Math.random() * 0.2
  }));
  publish("QUANTUM_COLLAPSE", { chosen: chosen.id, n: result.length });
  return { focus: chosen, field: result };
}
function cycle(tick = 0) {
  const signals = [
    { id: "alpha", amplitude: 0.88 - tick * 0.02 },
    { id: "beta", amplitude: 0.74 },
    { id: "delta", amplitude: 0.61 + tick * 0.01 }
  ];
  const field = superpose(signals);
  const { focus, field: collapsed } = observe(field);
  const avgEntropy = collapsed.reduce((s, x) => s + x.postEntropy, 0) / collapsed.length;
  console.log(`[q-attention] tick=${tick}  focus=${focus.id}  p=${focus.probability.toFixed(3)}  entropy=${avgEntropy.toFixed(3)}`);
  return { focus: focus.id, probability: +focus.probability.toFixed(3), entropy: +avgEntropy.toFixed(3) };
}
module.exports = { superpose, observe, cycle };
if (require.main === module) { console.log("QUANTUM ATTENTION…\n"); for (let t = 0; t < 5; t++) cycle(t); }
