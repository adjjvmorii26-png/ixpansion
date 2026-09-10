const { publish } = require("../../resonance_bus/bus.js");
function agent(id, strength = 0.7, rate = 0.08) {
  return { id, strength, rate, history: [strength] };
}
function step(a, entropy = 0.3) {
  const delta = a.rate * (0.5 - entropy) * (Math.random() * 0.6 + 0.7);
  let next = Math.max(0.1, Math.min(0.98, a.strength + delta));
  a.history.push(next);
  if (a.history.length > 20) a.history.shift();
  a.strength = next;
  publish("SELF_REWRITE", { id: a.id, strength: next, delta: +delta.toFixed(4) });
  return a;
}
function cycle(tick = 0) {
  const agents = [
    agent("scribe", 0.88, 0.06),
    agent("flux", 0.72, 0.12),
    agent("mirror", 0.80, 0.07),
    agent("void", 0.52, 0.15)
  ];
  const entropy = 0.25 + 0.1 * Math.sin(tick * 0.4);
  const after = agents.map(a => step({ ...a }, entropy));
  const avg = after.reduce((s, a) => s + a.strength, 0) / after.length;
  console.log(`[recursive] tick=${tick}  avg_strength=${avg.toFixed(3)}  entropy=${entropy.toFixed(3)}`);
  return { avg: +avg.toFixed(3), entropy: +entropy.toFixed(3), agents: after.map(a => ({ id: a.id, strength: +a.strength.toFixed(3) })) };
}
module.exports = { agent, step, cycle };
if (require.main === module) { console.log("RECURSIVE SELF…\n"); for (let t = 0; t < 5; t++) cycle(t); }
