const { publish } = require("../../resonance_bus/bus.js");
const buffer = [];
function clamp(n) { return Math.max(0, Math.min(1, +n || 0)); }
function dream(system, metrics = {}, intensity = 0.4) {
  const d = { system, dreamed: { strength: clamp((metrics.strength ?? 0.5) + (Math.random() - 0.4) * intensity), entropy: clamp((metrics.entropy ?? 0.3) + (Math.random() - 0.5) * intensity), coherence: clamp((metrics.coherence ?? 0.6) + (Math.random() - 0.5) * intensity * 0.5) }, intensity, ts: Date.now() };
  buffer.push(d); if (buffer.length > 30) buffer.shift();
  publish("DREAM", { system, strength: d.dreamed.strength });
  return d;
}
function contaminate(metrics, weight = 0.25) {
  if (!buffer.length) return { ...metrics, contaminated: false };
  const d = buffer[buffer.length - 1].dreamed;
  return { strength: clamp((metrics.strength ?? 0.5) * (1 - weight) + d.strength * weight), entropy: clamp((metrics.entropy ?? 0.3) * (1 - weight) + d.entropy * weight), coherence: clamp((metrics.coherence ?? 0.6) * (1 - weight) + d.coherence * weight), consensus: metrics.consensus ?? 0.5, contaminated: true };
}
function cycle(tick = 0) {
  const systems = ["attention", "quietus", "metamorph", "chronovore"];
  const sys = systems[tick % systems.length];
  const d = dream(sys, { strength: 0.6 + tick * 0.05, entropy: 0.3 }, 0.35);
  const after = contaminate({ strength: 0.7, entropy: 0.28, coherence: 0.65, consensus: 0.6 }, 0.3);
  console.log(`[dream] tick=${tick}  ${sys} dreamed str=${d.dreamed.strength.toFixed(3)}  → contaminated str=${after.strength.toFixed(3)}`);
  return { dream: d, contaminated: after };
}
module.exports = { dream, contaminate, recent: (n=5) => buffer.slice(-n), cycle, buffer };
if (require.main === module) { console.log("DREAM BUFFER…\n"); for (let t = 0; t < 4; t++) cycle(t); }
