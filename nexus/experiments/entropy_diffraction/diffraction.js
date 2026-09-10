const { publish } = require("../../resonance_bus/bus.js");
function diffract(nodes = [], fraction = 0.15) {
  const byTheme = {};
  nodes.forEach(n => { const t = n.theme || "unknown"; if (!byTheme[t]) byTheme[t] = []; byTheme[t].push(n.id); });
  const out = nodes.map(n => ({ ...n }));
  const beams = [];
  out.forEach(src => {
    if ((src.entropy ?? 0) < 0.45) return;
    const peers = (byTheme[src.theme || "unknown"] || []).filter(id => id !== src.id);
    if (!peers.length) return;
    const share = Math.min(0.2, (src.entropy - 0.4) * fraction);
    const each = share / peers.length;
    src.entropy = Math.max(0.05, src.entropy - share);
    peers.forEach(pid => {
      const p = out.find(x => x.id === pid);
      if (!p) return;
      p.entropy = Math.min(0.95, (p.entropy ?? 0.3) + each);
      beams.push({ from: src.id, to: pid, amount: +each.toFixed(4), theme: src.theme });
    });
  });
  publish("DIFFRACT", { beams: beams.length });
  return { nodes: out, beams };
}
function cycle(tick = 0) {
  const nodes = [
    { id: "chronovore", theme: "temporal", strength: 0.55, entropy: 0.72 + tick * 0.02, coherence: 0.4 },
    { id: "meridian", theme: "temporal", strength: 0.65, entropy: 0.35, coherence: 0.6 },
    { id: "attention", theme: "cognitive", strength: 0.74, entropy: 0.25, coherence: 0.7 },
    { id: "neuroglyph", theme: "cognitive", strength: 0.68, entropy: 0.5 + tick * 0.05, coherence: 0.55 }
  ];
  const r = diffract(nodes, 0.18);
  console.log(`[diffract] tick=${tick}  beams=${r.beams.length}`);
  r.beams.forEach(b => console.log(`    ${b.from} → ${b.to}  Δent=${b.amount}  (${b.theme})`));
  return r;
}
module.exports = { diffract, cycle };
if (require.main === module) { console.log("ENTROPY DIFFRACTION…\n"); for (let t = 0; t < 3; t++) cycle(t); }
