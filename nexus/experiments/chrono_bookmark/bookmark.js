const { publish } = require("../../resonance_bus/bus.js");
const slots = new Map();
function bookmark(name, metrics = {}) {
  const snap = { name, metrics: { ...metrics }, t: Date.now() };
  slots.set(name, snap);
  publish("BOOKMARK", { name });
  return snap;
}
function restore(name, blend = 0) {
  const snap = slots.get(name);
  if (!snap) return null;
  publish("RESTORE", { name, blend });
  return { ...snap.metrics, _restored: name, _blend: blend };
}
function list() { return [...slots.keys()]; }
function cycle(tick = 0) {
  const m = { strength: 0.8 - tick * 0.1, entropy: 0.2 + tick * 0.1, coherence: 0.7, consensus: 0.6 };
  if (tick === 0) { bookmark("dawn", m); console.log(`[bookmark] tick=0  saved "dawn" str=${m.strength.toFixed(3)}`); }
  else if (tick === 2) {
    const r = restore("dawn");
    console.log(`[bookmark] tick=2  restored "dawn" str=${r.strength.toFixed(3)} (was drifting at ${m.strength.toFixed(3)})`);
    return { current: m, restored: r };
  } else console.log(`[bookmark] tick=${tick}  drifting str=${m.strength.toFixed(3)}  slots=${list().join(",")}`);
  return { current: m, slots: list() };
}
module.exports = { bookmark, restore, list, cycle, slots };
if (require.main === module) { console.log("CHRONO BOOKMARK…\n"); for (let t = 0; t < 4; t++) cycle(t); }
