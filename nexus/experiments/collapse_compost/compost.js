const { publish } = require("../../resonance_bus/bus.js");
const { harvest } = require("../entropy_garden/garden.js");
function compost(echoes = []) {
  let fuel = 0;
  echoes.forEach(e => { fuel += (e.fragment ?? e.entropy ?? 0.4) * 0.25; });
  fuel = +Math.min(0.5, fuel).toFixed(3);
  publish("COMPOST", { fuel, n: echoes.length });
  return fuel;
}
function enrich(metrics, fuel) {
  let m = { ...metrics };
  m.entropy = Math.min(0.95, (m.entropy ?? 0.3) + fuel);
  m.strength = Math.max(0.1, (m.strength ?? 0.5) - fuel * 0.2);
  return { composted: m, harvest: harvest(m, 0.5), fuel };
}
function cycle(tick = 0) {
  const fuel = compost([{ source: "mesh", fragment: 0.55 }, { source: "quietus", fragment: 0.4 + tick * 0.05 }, { source: "paradox", fragment: 0.38 }]);
  const r = enrich({ strength: 0.65, entropy: 0.32, coherence: 0.6, consensus: 0.55 }, fuel);
  console.log(`[compost] tick=${tick}  fuel=${fuel}  ent=${r.composted.entropy.toFixed(3)}  harvested=${r.harvest.harvested}  h_fuel=${r.harvest.fuel}`);
  return r;
}
module.exports = { compost, enrich, cycle };
if (require.main === module) { console.log("COLLAPSE COMPOST…\n"); for (let t = 0; t < 4; t++) cycle(t); }
