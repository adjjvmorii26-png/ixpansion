const { publish } = require("../../resonance_bus/bus.js");
function overwrite(surface, underlayer, bleed = 0.15) {
  const result = {};
  ["strength", "entropy", "coherence", "consensus"].forEach(k => {
    result[k] = +(((surface[k] ?? 0.5) * (1 - bleed) + (underlayer[k] ?? 0.5) * bleed)).toFixed(4);
  });
  publish("PALIMPSEST", { bleed });
  return { surface: result, underlayer, bleed };
}
function cycle(tick = 0) {
  const under = { strength: 0.9, entropy: 0.1, coherence: 0.85, consensus: 0.8 };
  const surface = { strength: 0.4 + tick * 0.05, entropy: 0.55 - tick * 0.03, coherence: 0.45, consensus: 0.4 };
  const r = overwrite(surface, under, 0.12 + tick * 0.03);
  console.log(`[palimpsest] tick=${tick}  surface_str=${surface.strength.toFixed(3)}  after_bleed=${r.surface.strength}  (under=${under.strength})`);
  return r;
}
module.exports = { overwrite, cycle };
if (require.main === module) { console.log("PALIMPSEST…\n"); for (let t = 0; t < 4; t++) cycle(t); }
