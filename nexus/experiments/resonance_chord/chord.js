const { publish } = require("../../resonance_bus/bus.js");
function phase(m) { return (m.strength ?? 0.5) - (m.entropy ?? 0.3); }
function chord(members = [], lock = 0.25) {
  const phases = members.map(m => phase(m));
  const spread = Math.max(...phases) - Math.min(...phases);
  const locked = spread <= lock;
  publish(locked ? "CHORD_LOCK" : "CHORD_BREAK", { spread: +spread.toFixed(3) });
  return { phases: phases.map(p => +p.toFixed(3)), spread: +spread.toFixed(3), locked, mean: +(phases.reduce((a, b) => a + b, 0) / phases.length).toFixed(3) };
}
function cycle(tick = 0) {
  const members = [
    { name: "alpha", strength: 0.72, entropy: 0.28 + tick * 0.04 },
    { name: "beta", strength: 0.68 - tick * 0.03, entropy: 0.30 },
    { name: "delta", strength: 0.70, entropy: 0.25 + tick * 0.05 }
  ];
  const r = chord(members, 0.22);
  console.log(`[chord] tick=${tick}  phases=[${r.phases.join(", ")}]  spread=${r.spread}  locked=${r.locked}`);
  return { members, ...r };
}
module.exports = { phase, chord, cycle };
if (require.main === module) { console.log("RESONANCE CHORD…\n"); for (let t = 0; t < 5; t++) cycle(t); }
