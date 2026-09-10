const { publish } = require("../../resonance_bus/bus.js");
function twin(metrics = {}) {
  return { strength: +(1 - (metrics.strength ?? 0.5)).toFixed(4), entropy: +(1 - (metrics.entropy ?? 0.3)).toFixed(4), coherence: +(1 - (metrics.coherence ?? 0.6)).toFixed(4), consensus: +(1 - (metrics.consensus ?? 0.5)).toFixed(4), shadow: true };
}
function divergence(primary, shadow) {
  return +(Math.abs(primary.strength - (1 - shadow.strength)) + Math.abs(primary.entropy - (1 - shadow.entropy))).toFixed(4);
}
function cycle(tick = 0) {
  const primary = { strength: 0.7 + tick * 0.04, entropy: 0.25 + tick * 0.03, coherence: 0.65, consensus: 0.6 };
  const shadow = twin(primary);
  shadow.strength = Math.max(0, Math.min(1, shadow.strength + (Math.random() - 0.5) * 0.1));
  const div = divergence(primary, shadow);
  const fractured = div > 0.15;
  if (fractured) publish("MIRROR_FRACTURE", { div });
  console.log(`[mirror] tick=${tick}  primary_str=${primary.strength.toFixed(3)}  shadow_str=${shadow.strength.toFixed(3)}  div=${div}  fractured=${fractured}`);
  return { primary, shadow, div, fractured };
}
module.exports = { twin, divergence, cycle };
if (require.main === module) { console.log("MIRROR TWIN…\n"); for (let t = 0; t < 4; t++) cycle(t); }
