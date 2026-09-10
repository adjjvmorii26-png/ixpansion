#!/usr/bin/env node
/**
 * Astral Forge — Shell
 * Outer executable boundary. Boots lattice → crucible → choir.
 */

const fs = require('fs');
const path = require('path');
const { forge } = require('../crucible/crucible_core.js');

const CONFIG = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'astral.config'), 'utf8'));

let tick = 0;
const MAX_TICKS = 24;

function loadShardResonance() {
  const dir = path.join(__dirname, '..', 'lattice', 'memory_crystals');
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.lx'));
  return files.map(f => {
    const txt = fs.readFileSync(path.join(dir, f), 'utf8');
    const m = txt.match(/resonance:\s*([\d.]+)/);
    return m ? parseFloat(m[1]) : 0.5;
  });
}

function choirVote(state) {
  // Simplified harmonic majority
  const agents = {
    alpha: 0.86 + (Math.random() - 0.5) * 0.06,
    beta:  0.89 + (Math.random() - 0.5) * 0.05,
    gamma: 0.84 + (Math.random() - 0.5) * 0.07,
    void:  0.55 + (Math.random() - 0.5) * 0.15
  };
  const affirm = Object.values(agents).filter(s => s > 0.62).length;
  const avg = Object.values(agents).reduce((a, b) => a + b, 0) / 4;
  return { agents, affirm, avg: +avg.toFixed(3), consensus: affirm >= 3 && avg >= CONFIG.lattice.resonance_threshold };
}

async function cycle() {
  const resonances = loadShardResonance();
  const state = {
    alpha: resonances[0] || 0.8,
    beta:  resonances[1] || 0.8,
    gamma: resonances[2] || 0.7
  };

  const distortion = ['fold', 'shear', 'liquefy', 'bloom'][tick % 4];
  const forged = forge(state, distortion);
  const vote = choirVote(forged);

  console.log(`[shell] tick=${tick.toString().padStart(2)}  dist=${distortion.padEnd(7)}  temp=${forged.temperature}  choir_avg=${vote.avg}  consensus=${vote.consensus}`);
  return { forged, vote };
}

async function main() {
  console.log('ASTRAL FORGE shell booting…');
  console.log(`Lattice heartbeat target: ${CONFIG.lattice.heartbeat_ms}ms`);
  console.log('Sequence: lattice → crucible → choir\n');

  while (tick < MAX_TICKS) {
    await cycle();
    tick++;
    await new Promise(r => setTimeout(r, CONFIG.lattice.heartbeat_ms));
  }

  console.log('\nShell cycle complete. Lattice remains resonant.');
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { cycle };
