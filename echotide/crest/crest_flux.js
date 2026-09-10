/**
 * Echotide Engine — Crest Flux
 * Generates new wave forms under cantor consensus and abyss pressure awareness.
 */

const fs = require('fs');
const path = require('path');
const { cycle: abyssCycle } = require('../abyss/abyss_core.js');

const CONFIG = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'echotide.config'), 'utf8'));

function loadResonances() {
  const dir = path.join(__dirname, '..', 'reef', 'wave_crystals');
  return fs.readdirSync(dir)
    .filter(f => f.endsWith('.wx'))
    .map(f => {
      const txt = fs.readFileSync(path.join(dir, f), 'utf8');
      const m = txt.match(/resonance:\s*([\d.]+)/);
      return m ? parseFloat(m[1]) : 0.5;
    });
}

function cantorConsensus(pressure, resonances) {
  const avgRes = resonances.reduce((a, b) => a + b, 0) / Math.max(1, resonances.length);
  const agents = {
    echo:   0.86 + (Math.random() - 0.5) * 0.05,
    shift:  0.82 + (Math.random() - 0.5) * 0.06,
    mirror: 0.79 + (Math.random() - 0.5) * 0.07,
    null:   0.50 + (Math.random() - 0.5) * 0.12 - pressure * 0.08
  };
  const affirm = Object.values(agents).filter(s => s > 0.58).length;
  const avg = Object.values(agents).reduce((a, b) => a + b, 0) / 4;
  return {
    agents,
    avg: +avg.toFixed(3),
    consensus: affirm >= 3 && avg >= CONFIG.reef.resonance_threshold
  };
}

function birthChance(pressure, consensus) {
  if (!consensus) return 0;
  return Math.max(0, CONFIG.crest.birth_probability * (1 - pressure * 0.4));
}

async function cycle(tick) {
  const abyss = abyssCycle(tick);
  const resonances = loadResonances();
  const vote = cantorConsensus(abyss.pressure, resonances);
  const chance = birthChance(abyss.pressure, vote.consensus);
  const born = Math.random() < chance;

  console.log(`[crest] tick=${String(tick).padStart(2)}  pressure=${abyss.pressure}  choir_avg=${vote.avg}  consensus=${vote.consensus}  birth=${born ? 'YES' : 'no '}  chance=${chance.toFixed(2)}`);
  return { abyss, vote, born, chance: +chance.toFixed(3) };
}

async function main() {
  console.log('ECHOTIDE crest flux online…');
  console.log(`Flux interval: ${CONFIG.crest.flux_interval_ms}ms  Birth p: ${CONFIG.crest.birth_probability}\n`);

  for (let t = 0; t < 18; t++) {
    await cycle(t);
    await new Promise(r => setTimeout(r, CONFIG.crest.flux_interval_ms));
  }
  console.log('\nCrest cycle complete. Tide continues.');
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { cycle };
