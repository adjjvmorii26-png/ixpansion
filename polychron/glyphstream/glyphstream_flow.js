/**
 * Polychron Atlas — Glyphstream Flow
 * Advances symbolic temporal inscriptions.
 */

const fs = require('fs');
const path = require('path');

const CONFIG = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'polychron.config'), 'utf8'));
const GLYPHS_DIR = path.join(__dirname, 'glyphs');

function loadGlyphs() {
  return fs.readdirSync(GLYPHS_DIR)
    .filter(f => f.endsWith('.gs'))
    .map(f => {
      const txt = fs.readFileSync(path.join(GLYPHS_DIR, f), 'utf8');
      const weight = parseFloat((txt.match(/temporal_weight:\s*([\d.]+)/) || [])[1] || 0.5);
      const entropy = parseFloat((txt.match(/entropy_at_inscribe:\s*([\d.]+)/) || [])[1] || 0.3);
      return { file: f, weight, entropy };
    });
}

function flow(tick = 0) {
  const glyphs = loadGlyphs();
  const avgWeight = glyphs.reduce((s, g) => s + g.weight, 0) / Math.max(1, glyphs.length);
  const avgEntropy = glyphs.reduce((s, g) => s + g.entropy, 0) / Math.max(1, glyphs.length);
  const drift = 0.05 * Math.sin(tick * 0.21);
  const coherence = Math.max(0, avgWeight - avgEntropy * 0.8 + drift);

  console.log(`[glyph] tick=${String(tick).padStart(2)}  weight=${avgWeight.toFixed(3)}  entropy=${avgEntropy.toFixed(3)}  coherence=${coherence.toFixed(3)}`);
  return { avgWeight: +avgWeight.toFixed(3), avgEntropy: +avgEntropy.toFixed(3), coherence: +coherence.toFixed(3), count: glyphs.length };
}

module.exports = { flow, loadGlyphs };

if (require.main === module) {
  console.log('GLYPHSTREAM flow online…\n');
  for (let t = 0; t < 10; t++) flow(t);
}
