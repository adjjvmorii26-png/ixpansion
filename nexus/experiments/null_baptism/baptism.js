const { publish } = require("../../resonance_bus/bus.js");
const state = new Map();
function baptize(id, metric = "entropy", baseline = 0.3) {
  state.set(id, { metric, baseline, tick: 0, active: true });
  publish("BAPTISM", { id, metric });
  return { id, metric, baseline, phase: "null" };
}
function recover(nodes = [], rate = 0.22) {
  const out = nodes.map(n => ({ ...n }));
  const log = [];
  out.forEach(n => {
    const s = state.get(n.id);
    if (!s || !s.active) return;
    s.tick += 1;
    const t = s.tick;
    const value = t === 1 ? 0.02 : s.baseline * (1 - Math.exp(-rate * (t - 1)));
    n[s.metric] = Math.min(0.95, Math.max(0.02, +value.toFixed(4)));
    log.push({ id: n.id, metric: s.metric, value: n[s.metric], tick: t });
    if (t >= 6) s.active = false;
  });
  return { nodes: out, log };
}
function cycle(tick = 0) {
  const nodes = [
    { id: "void", strength: 0.45, entropy: 0.7, coherence: 0.4 },
    { id: "quietus", strength: 0.5, entropy: 0.55, coherence: 0.45 }
  ];
  if (tick === 0) { baptize("void", "entropy", 0.55); console.log(`[baptism] tick=0  null void.entropy`); }
  const r = recover(nodes);
  console.log(`[baptism] tick=${tick}  recoveries=${r.log.length}`);
  r.log.forEach(l => console.log(`    ${l.id}.${l.metric}=${l.value}  (t=${l.tick})`));
  return r;
}
module.exports = { baptize, recover, cycle, state };
if (require.main === module) { console.log("NULL BAPTISM…\n"); for (let t = 0; t < 5; t++) cycle(t); }
