const crystals = require("./crystal_store.js");
const THEME_SAMPLES = {
  cognitive: [{ strength: 0.78, entropy: 0.22 }, { strength: 0.72, entropy: 0.28 }, { strength: 0.68, entropy: 0.34 }, { strength: 0.64, entropy: 0.40 }],
  temporal: [{ strength: 0.70, entropy: 0.30 }, { strength: 0.62, entropy: 0.40 }, { strength: 0.55, entropy: 0.48 }, { strength: 0.48, entropy: 0.55 }],
  ontological: [{ strength: 0.60, entropy: 0.35 }, { strength: 0.52, entropy: 0.45 }, { strength: 0.44, entropy: 0.55 }, { strength: 0.38, entropy: 0.62 }],
  transformative: [{ strength: 0.75, entropy: 0.25 }, { strength: 0.65, entropy: 0.35 }, { strength: 0.55, entropy: 0.42 }, { strength: 0.48, entropy: 0.50 }],
  spatial: [{ strength: 0.80, entropy: 0.18 }, { strength: 0.74, entropy: 0.24 }, { strength: 0.70, entropy: 0.30 }, { strength: 0.66, entropy: 0.34 }],
  linguistic: [{ strength: 0.72, entropy: 0.20 }, { strength: 0.70, entropy: 0.24 }, { strength: 0.68, entropy: 0.28 }, { strength: 0.66, entropy: 0.30 }]
};
function seed() {
  let n = 0;
  Object.entries(THEME_SAMPLES).forEach(([theme, samples]) => {
    samples.forEach((m, i) => {
      crystals.seal(`hist_${theme}_${i}`, { strength: m.strength, entropy: m.entropy, coherence: m.strength * 0.9, consensus: m.strength * 0.85 }, { theme, label: `${theme} history ${i}`, synthetic: true });
      n++;
    });
  });
  const sum = crystals.summary();
  console.log(`[seed] sealed ${n} history crystals  total=${sum.count}  avgS=${sum.avgStrength}  avgE=${sum.avgEntropy}`);
  return sum;
}
module.exports = { seed, THEME_SAMPLES };
if (require.main === module) seed();
