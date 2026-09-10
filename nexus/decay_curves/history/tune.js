const crystals = require("../../memory_crystals/crystal_store.js");
const { THEMES } = require("../curves.js");
function snapshotThemes() {
  const data = crystals.load();
  const byTheme = {};
  Object.values(data.crystals || {}).forEach(c => {
    const theme = c.payload?.theme || "default";
    if (!byTheme[theme]) byTheme[theme] = [];
    byTheme[theme].push(c.metrics);
  });
  return byTheme;
}
function recommend(byTheme) {
  const rec = {};
  Object.entries(byTheme).forEach(([theme, samples]) => {
    if (!samples.length) return;
    const avgE = samples.reduce((s, m) => s + (m.entropy || 0), 0) / samples.length;
    const avgS = samples.reduce((s, m) => s + (m.strength || 0), 0) / samples.length;
    const base = THEMES[theme] || THEMES.default;
    const entropyRise = avgE > 0.55 ? base.entropyRise * 0.7 : avgE < 0.3 ? base.entropyRise * 1.2 : base.entropyRise;
    const strengthDecay = avgS < 0.4 ? base.strengthDecay * 0.7 : avgS > 0.75 ? base.strengthDecay * 1.15 : base.strengthDecay;
    rec[theme] = { strengthDecay: +strengthDecay.toFixed(4), entropyRise: +entropyRise.toFixed(4), coherenceDecay: base.coherenceDecay, label: base.label + " (tuned)", samples: samples.length, avgStrength: +avgS.toFixed(3), avgEntropy: +avgE.toFixed(3) };
  });
  return rec;
}
function applyTuned(metrics, theme, ticks = 1) {
  const rec = recommend(snapshotThemes());
  const c = rec[theme] || THEMES[theme] || THEMES.default;
  let { strength = 0.5, entropy = 0.3, coherence = 0.6, consensus = 0.5 } = metrics;
  for (let i = 0; i < ticks; i++) {
    strength = Math.max(0, strength - c.strengthDecay * (0.85 + Math.random() * 0.3));
    entropy = Math.min(1, entropy + c.entropyRise * (0.85 + Math.random() * 0.3));
    coherence = Math.max(0, coherence - (c.coherenceDecay || 0.04) * (0.85 + Math.random() * 0.3));
    consensus = Math.max(0, Math.min(1, consensus * 0.98 + (strength - entropy) * 0.02));
  }
  return { strength: +strength.toFixed(4), entropy: +entropy.toFixed(4), coherence: +coherence.toFixed(4), consensus: +consensus.toFixed(4), theme, tuned: !!rec[theme], label: c.label };
}
function cycle(tick = 0) {
  const rec = recommend(snapshotThemes());
  console.log(`[tune] tick=${tick}  themes=${Object.keys(rec).length}`);
  Object.entries(rec).forEach(([t, r]) => console.log(`  ${t.padEnd(14)} n=${r.samples} avgS=${r.avgStrength} avgE=${r.avgEntropy}`));
  return { recommendations: rec };
}
module.exports = { snapshotThemes, recommend, applyTuned, cycle };
