const fs = require("fs");
const path = require("path");
const { normalize } = require("../adapters/normalize.js");
const ARTIFACTS = path.resolve(__dirname, "../../../");
const SIBLINGS = {
  "attention-labyrinth": "attention_labyrinth/interfaces/labyrinth_terminal.js",
  "quietus-array": "quietus_array/interfaces/quietus_terminal.js",
  "metamorph-forge": "metamorph_forge/interfaces/metamorph_terminal.js",
  "probability-engine": "probability_engine/interfaces/probability_terminal.js",
  "chronovore-archive": "chronovore_archive/interfaces/chronovore_terminal.js",
  "neuroglyph-forge": "neuroglyph_forge/interfaces/neuroglyph_terminal.js"
};
function probePath(rel) { return path.join(ARTIFACTS, rel); }
function available() {
  return Object.entries(SIBLINGS).filter(([, rel]) => fs.existsSync(probePath(rel))).map(([name]) => name);
}
function synthetic(name) {
  let h = 0;
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) | 0;
  const strength = 0.4 + (Math.abs(h) % 50) / 100;
  const entropy = 0.2 + (Math.abs(h >> 3) % 40) / 100;
  return normalize({ strength, entropy, coherence: strength * 0.9, consensus: strength * 0.8 });
}
function probe(name) {
  const rel = SIBLINGS[name];
  if (!rel || !fs.existsSync(probePath(rel))) return { name, source: "synthetic", metrics: synthetic(name) };
  try {
    const stat = fs.statSync(probePath(rel));
    const ageMin = (Date.now() - stat.mtimeMs) / 60000;
    const strength = Math.max(0.3, Math.min(0.95, 0.9 - ageMin * 0.01));
    return { name, source: "live", path: rel, metrics: normalize({ strength, entropy: 0.25 + ageMin * 0.005, coherence: strength * 0.92 }) };
  } catch (e) {
    return { name, source: "synthetic", metrics: synthetic(name), error: e.message };
  }
}
function probeAll() { return Object.keys(SIBLINGS).map(probe); }
function cycle(tick = 0) {
  const results = probeAll();
  const live = results.filter(r => r.source === "live").length;
  const avgS = results.reduce((s, r) => s + r.metrics.strength, 0) / results.length;
  console.log(`[probe] tick=${tick}  live=${live}/${results.length}  avg_strength=${avgS.toFixed(3)}`);
  results.forEach(r => console.log(`  ${r.name.padEnd(22)} ${r.source.padEnd(10)} str=${r.metrics.strength.toFixed(3)} ent=${r.metrics.entropy.toFixed(3)}`));
  return { live, total: results.length, avgStrength: +avgS.toFixed(3), results };
}
module.exports = { available, probe, probeAll, synthetic, cycle, SIBLINGS };
