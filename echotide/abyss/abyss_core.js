/**
 * Echotide Engine — Abyss Core
 * Monitors pressure, records collapses, applies void damping.
 */

const fs = require('fs');
const path = require('path');

const CONFIG = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'echotide.config'), 'utf8'));
const DECAYS_DIR = path.join(__dirname, 'decays');

function listDecays() {
  return fs.readdirSync(DECAYS_DIR)
    .filter(f => f.endsWith('.ab'))
    .map(f => {
      const txt = fs.readFileSync(path.join(DECAYS_DIR, f), 'utf8');
      const peak = parseFloat((txt.match(/peak_pressure:\s*([\d.]+)/) || [])[1] || 0.5);
      return { file: f, peak };
    });
}

function samplePressure(tick) {
  const base = 0.45 + 0.25 * Math.sin(tick * 0.19);
  const noise = (Math.random() - 0.5) * 0.18;
  return Math.max(0.1, Math.min(CONFIG.abyss.pressure_cap, base + noise));
}

function cycle(tick) {
  const pressure = samplePressure(tick);
  const decays = listDecays();
  const avgPeak = decays.reduce((s, d) => s + d.peak, 0) / Math.max(1, decays.length);
  const risk = pressure > CONFIG.abyss.collapse_threshold;
  const damping = CONFIG.abyss.void_damping * (risk ? 1.4 : 1.0);

  console.log(`[abyss] tick=${String(tick).padStart(2)}  pressure=${pressure.toFixed(3)}  risk=${risk}  damping=${damping.toFixed(3)}  decays=${decays.length}`);
  return { pressure: +pressure.toFixed(3), risk, damping: +damping.toFixed(3), decays: decays.length };
}

module.exports = { cycle, listDecays, samplePressure };

if (require.main === module) {
  console.log('ABYS S core online…\n');
  for (let t = 0; t < 12; t++) cycle(t);
}
