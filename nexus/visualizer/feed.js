const { recent } = require("../resonance_bus/bus.js");
function bar(n, width = 12) {
  const filled = Math.round(Math.max(0, Math.min(1, n)) * width);
  return "█".repeat(filled) + "░".repeat(width - filled);
}
function frame(label, metrics = {}) {
  const s = metrics.strength ?? 0, e = metrics.entropy ?? 0, c = metrics.coherence ?? 0, v = metrics.consensus ?? 0;
  return { t: Date.now(), label, metrics: { strength: s, entropy: e, coherence: c, consensus: v },
    ascii: [`  str ${bar(s)} ${s.toFixed(3)}`, `  ent ${bar(e)} ${e.toFixed(3)}`, `  coh ${bar(c)} ${c.toFixed(3)}`, `  con ${bar(v)} ${v.toFixed(3)}`].join("\n") };
}
function render(frames = []) {
  frames.forEach(f => { console.log(`┌─ ${f.label}`); console.log(f.ascii); console.log("└──────────────"); });
}
function cycle(tick = 0) {
  const frames = [
    frame("quantum", { strength: 0.7 - tick * 0.05, entropy: 0.3 + tick * 0.04, coherence: 0.65, consensus: 0.6 }),
    frame("mesh", { strength: 0.75, entropy: 0.28, coherence: 0.8, consensus: 0.86 - tick * 0.01 }),
    frame("recursive", { strength: 0.75 - tick * 0.01, entropy: 0.25 + tick * 0.03, coherence: 0.7, consensus: 0.55 })
  ];
  console.log(`[viz] tick=${tick}`);
  render(frames);
  const bus = recent(3);
  if (bus.length) { console.log("  bus:"); bus.forEach(e => console.log(`    ${e.event}`)); }
  return frames;
}
module.exports = { bar, frame, render, cycle };
if (require.main === module) { console.log("VISUALIZER FEED…\n"); for (let t = 0; t < 3; t++) { cycle(t); console.log(); } }
