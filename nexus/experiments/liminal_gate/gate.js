const { publish } = require("../../resonance_bus/bus.js");
let lastSide = null;
function check(metrics, threshold = 0.5) {
  const s = metrics.strength ?? 0.5;
  const side = s >= threshold ? "above" : "below";
  let event = null;
  if (lastSide && lastSide !== side) {
    event = side === "above" ? "EMERGENCE" : "RECESSION";
    publish("LIMINAL", { event, strength: s, threshold });
  }
  lastSide = side;
  return { side, event, strength: s, threshold };
}
function cycle(tick = 0) {
  const strength = Math.max(0.05, Math.min(0.95, 0.35 + 0.4 * Math.sin(tick * 0.9)));
  const r = check({ strength }, 0.5);
  console.log(`[liminal] tick=${tick}  str=${r.strength.toFixed(3)}  side=${r.side}${r.event ? " ★ " + r.event : ""}`);
  return r;
}
function reset() { lastSide = null; }
module.exports = { check, cycle, reset };
if (require.main === module) { console.log("LIMINAL GATE…\n"); for (let t = 0; t < 10; t++) cycle(t); }
