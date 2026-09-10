const { publish } = require("../../resonance_bus/bus.js");
function pair(a, b, transfer = 0.15) {
  const donated = Math.min(a.strength * transfer, 0.2);
  const result = { a: { strength: Math.max(0.1, a.strength - donated), entropy: Math.min(1, (a.entropy ?? 0.3) + donated * 0.3), coherence: a.coherence ?? 0.6, consensus: a.consensus ?? 0.5 }, b: { strength: b.strength ?? 0.5, entropy: b.entropy ?? 0.3, coherence: Math.min(0.98, (b.coherence ?? 0.5) + donated * 1.2), consensus: Math.min(0.98, (b.consensus ?? 0.5) + donated * 0.5) }, donated: +donated.toFixed(4) };
  publish("SYMBIOSIS", { donated: result.donated });
  return result;
}
function cycle(tick = 0) {
  const host = { strength: 0.8 - tick * 0.05, entropy: 0.25, coherence: 0.7, consensus: 0.65 };
  const guest = { strength: 0.45, entropy: 0.4, coherence: 0.4, consensus: 0.35 };
  const r = pair(host, guest, 0.12 + tick * 0.02);
  console.log(`[symbiosis] tick=${tick}  donated=${r.donated}  host_str=${r.a.strength.toFixed(3)}  guest_coh=${r.b.coherence.toFixed(3)}`);
  return r;
}
module.exports = { pair, cycle };
if (require.main === module) { console.log("SYMBIOSIS…\n"); for (let t = 0; t < 4; t++) cycle(t); }
