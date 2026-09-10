const THEMES = {
  temporal:     { strengthDecay: 0.06, entropyRise: 0.08, coherenceDecay: 0.04, label: "time erodes" },
  linguistic:   { strengthDecay: 0.03, entropyRise: 0.05, coherenceDecay: 0.02, label: "meaning drifts" },
  spatial:      { strengthDecay: 0.04, entropyRise: 0.04, coherenceDecay: 0.03, label: "geometry softens" },
  cognitive:    { strengthDecay: 0.05, entropyRise: 0.07, coherenceDecay: 0.05, label: "attention frays" },
  ontological:  { strengthDecay: 0.07, entropyRise: 0.09, coherenceDecay: 0.06, label: "being thins" },
  transformative: { strengthDecay: 0.08, entropyRise: 0.06, coherenceDecay: 0.04, label: "form sheds" },
  default:      { strengthDecay: 0.05, entropyRise: 0.06, coherenceDecay: 0.04, label: "generic decay" }
};
function curve(theme = "default") { return THEMES[theme] || THEMES.default; }
function apply(metrics, theme = "default", ticks = 1) {
  const c = curve(theme);
  let { strength = 0.5, entropy = 0.3, coherence = 0.6, consensus = 0.5 } = metrics;
  for (let i = 0; i < ticks; i++) {
    strength = Math.max(0, strength - c.strengthDecay * (0.8 + Math.random() * 0.4));
    entropy = Math.min(1, entropy + c.entropyRise * (0.8 + Math.random() * 0.4));
    coherence = Math.max(0, coherence - c.coherenceDecay * (0.8 + Math.random() * 0.4));
    consensus = Math.max(0, Math.min(1, consensus * 0.98 + (strength - entropy) * 0.02));
  }
  return { strength: +strength.toFixed(4), entropy: +entropy.toFixed(4), coherence: +coherence.toFixed(4), consensus: +consensus.toFixed(4), theme, label: c.label };
}
function cycle(tick = 0) {
  const themes = Object.keys(THEMES).filter(t => t !== "default");
  const theme = themes[tick % themes.length];
  const after = apply({ strength: 0.8, entropy: 0.2, coherence: 0.75, consensus: 0.7 }, theme, 1 + (tick % 3));
  console.log(`[decay] tick=${tick}  theme=${theme.padEnd(14)}  str=${after.strength}  ent=${after.entropy}  (${after.label})`);
  return after;
}
module.exports = { THEMES, curve, apply, cycle };
