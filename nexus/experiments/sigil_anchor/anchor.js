const { publish } = require("../../resonance_bus/bus.js");
const sigils = new Map();
function plant(name, id, metrics = {}, ttl = 4) {
  sigils.set(name, { id, metrics: { strength: metrics.strength ?? 0.7, coherence: metrics.coherence ?? 0.7 }, ttl, born: Date.now() });
  publish("SIGIL_PLANT", { name, id, ttl });
  return sigils.get(name);
}
function apply(nodes = []) {
  const out = nodes.map(n => ({ ...n }));
  const active = [];
  for (const [name, s] of [...sigils.entries()]) {
    if (s.ttl <= 0) { sigils.delete(name); publish("SIGIL_FADE", { name }); continue; }
    const n = out.find(x => x.id === s.id);
    if (n) {
      n.strength = +(n.strength * 0.4 + s.metrics.strength * 0.6).toFixed(4);
      n.coherence = +((n.coherence ?? 0.5) * 0.4 + s.metrics.coherence * 0.6).toFixed(4);
      active.push({ name, id: s.id, ttl: s.ttl });
    }
    s.ttl -= 1;
  }
  publish("SIGIL_HOLD", { n: active.length });
  return { nodes: out, active };
}
function cycle(tick = 0) {
  const nodes = [
    { id: "gate", strength: 0.4 + tick * 0.02, entropy: 0.5, coherence: 0.35 },
    { id: "chorus", strength: 0.6, entropy: 0.3, coherence: 0.55 }
  ];
  if (tick === 0) { plant("golden_seal", "gate", { strength: 0.82, coherence: 0.78 }, 3); console.log(`[sigil] planted golden_seal on gate`); }
  const r = apply(nodes);
  console.log(`[sigil] tick=${tick}  active=${r.active.length}`);
  r.active.forEach(a => console.log(`    ${a.name}@${a.id} ttl=${a.ttl}`));
  const g = r.nodes.find(n => n.id === "gate");
  if (g) console.log(`    gate str=${g.strength} coh=${g.coherence}`);
  return r;
}
module.exports = { plant, apply, cycle, sigils };
if (require.main === module) { console.log("SIGIL ANCHOR…\n"); sigils.clear(); for (let t = 0; t < 5; t++) cycle(t); }
