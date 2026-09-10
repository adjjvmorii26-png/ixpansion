const { publish } = require("../../resonance_bus/bus.js");
function plant(metrics, water = 0.08) {
  return { strength: Math.max(0.15, (metrics.strength ?? 0.5) - water * 0.3), entropy: Math.min(0.95, (metrics.entropy ?? 0.3) + water), coherence: Math.max(0.1, (metrics.coherence ?? 0.6) - water * 0.4), consensus: metrics.consensus ?? 0.5, watered: water };
}
function harvest(metrics, threshold = 0.55) {
  if ((metrics.entropy ?? 0) < threshold) return { harvested: false, fuel: 0, metrics };
  const fuel = +((metrics.entropy - threshold) * 1.5).toFixed(3);
  const after = { strength: Math.min(0.95, (metrics.strength ?? 0.5) + fuel * 0.4), entropy: threshold, coherence: Math.min(0.95, (metrics.coherence ?? 0.5) + fuel * 0.3), consensus: metrics.consensus ?? 0.5 };
  publish("GARDEN_HARVEST", { fuel });
  return { harvested: true, fuel, metrics: after };
}
function cycle(tick = 0) {
  let m = { strength: 0.7, entropy: 0.3, coherence: 0.65, consensus: 0.6 };
  for (let i = 0; i < 2 + tick; i++) m = plant(m, 0.07);
  const h = harvest(m, 0.5);
  console.log(`[garden] tick=${tick}  ent=${m.entropy.toFixed(3)}  harvested=${h.harvested}  fuel=${h.fuel}`);
  if (h.harvested) console.log(`    after harvest str=${h.metrics.strength.toFixed(3)} ent=${h.metrics.entropy.toFixed(3)}`);
  return { grown: m, ...h };
}
module.exports = { plant, harvest, cycle };
if (require.main === module) { console.log("ENTROPY GARDEN…\n"); for (let t = 0; t < 4; t++) cycle(t); }
