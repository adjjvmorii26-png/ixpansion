const { publish } = require("../../resonance_bus/bus.js");
function phase(tick, period = 8) { return (tick % period) / period; }
function envelope(p) { return 0.7 + 0.45 * (0.5 + 0.5 * Math.sin(p * Math.PI * 2)); }
function apply(metrics, tick, period = 8) {
  const p = phase(tick, period);
  const env = envelope(p);
  const out = {
    ...metrics,
    strength: +Math.max(0.05, Math.min(0.99, (metrics.strength ?? 0.5) * env)).toFixed(4),
    entropy: +Math.max(0.05, Math.min(0.99, (metrics.entropy ?? 0.3) * (2 - env))).toFixed(4),
    coherence: metrics.coherence ?? 0.6,
    consensus: metrics.consensus ?? 0.5,
    tide: +env.toFixed(3),
    phase: +p.toFixed(3)
  };
  publish("TIDE", { phase: out.phase, envelope: out.tide });
  return out;
}
function cycle(tick = 0) {
  const after = apply({ strength: 0.7, entropy: 0.3, coherence: 0.65, consensus: 0.6 }, tick);
  console.log(`[tide] tick=${tick}  phase=${after.phase}  env=${after.tide}  str=${after.strength.toFixed(3)}  ent=${after.entropy.toFixed(3)}`);
  return after;
}
module.exports = { phase, envelope, apply, cycle };
if (require.main === module) { console.log("TIDE CLOCK…\n"); for (let t = 0; t < 8; t++) cycle(t); }
