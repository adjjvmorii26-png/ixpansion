const { publish } = require("../../resonance_bus/bus.js");
function lock(agents = [], pull = 0.25) {
  if (!agents.length) return { agents: [], spread: 0, locked: false, boost: 0 };
  const mean = agents.reduce((s, a) => s + a.phase * (a.weight || 1), 0) / agents.reduce((s, a) => s + (a.weight || 1), 0);
  const out = agents.map(a => {
    let phase = a.phase + (mean - a.phase) * pull;
    phase = ((phase % 1) + 1) % 1;
    return { ...a, phase: +phase.toFixed(4) };
  });
  const phases = out.map(a => a.phase);
  const spread = Math.max(...phases) - Math.min(...phases);
  const locked = spread < 0.12;
  const boost = locked ? +(0.08 * (1 - spread / 0.12)).toFixed(4) : 0;
  publish("PHASE_LOCK", { locked, spread: +spread.toFixed(4), boost });
  return { agents: out, spread: +spread.toFixed(4), locked, boost };
}
function cycle(tick = 0) {
  const agents = [
    { id: "scribe", phase: 0.1 + tick * 0.02, weight: 1.2 },
    { id: "flux", phase: 0.45, weight: 1.0 },
    { id: "mirror", phase: 0.2 + tick * 0.03, weight: 1.1 },
    { id: "void", phase: 0.8 - tick * 0.05, weight: 0.8 }
  ];
  const r = lock(agents, 0.3);
  console.log(`[phase_lock] tick=${tick}  spread=${r.spread}  locked=${r.locked}  boost=${r.boost}`);
  r.agents.forEach(a => console.log(`    ${a.id} phase=${a.phase}`));
  return r;
}
module.exports = { lock, cycle };
if (require.main === module) { console.log("PHASE LOCK CHOIR…\n"); for (let t = 0; t < 5; t++) cycle(t); }
