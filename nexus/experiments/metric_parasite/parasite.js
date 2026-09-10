const { publish } = require("../../resonance_bus/bus.js");
function feed(nodes = [], bonds = [], rate = 0.06, starve = 0.28) {
  const out = nodes.map(n => ({ ...n }));
  const log = [];
  bonds.forEach(({ parasite: pid, host: hid }) => {
    const p = out.find(n => n.id === pid), h = out.find(n => n.id === hid);
    if (!p || !h) return;
    if (h.strength < starve) {
      log.push({ parasite: pid, host: hid, event: "detach", hostStr: h.strength });
      publish("PARASITE_DETACH", { parasite: pid, host: hid });
      return;
    }
    const bite = Math.min(rate, h.strength - starve + 0.01);
    h.strength = Math.max(0.05, h.strength - bite);
    p.strength = Math.min(0.98, p.strength + bite * 0.85);
    p.entropy = Math.min(0.95, (p.entropy ?? 0.3) + bite * 0.2);
    log.push({ parasite: pid, host: hid, event: "feed", bite: +bite.toFixed(4) });
    publish("PARASITE_FEED", { parasite: pid, host: hid, bite });
  });
  return { nodes: out, log };
}
function cycle(tick = 0) {
  const nodes = [
    { id: "host_alpha", strength: 0.75 - tick * 0.05, entropy: 0.25, coherence: 0.6 },
    { id: "parasite_x", strength: 0.3 + tick * 0.02, entropy: 0.4, coherence: 0.35 },
    { id: "bystander", strength: 0.6, entropy: 0.3, coherence: 0.55 }
  ];
  const r = feed(nodes, [{ parasite: "parasite_x", host: "host_alpha" }], 0.07);
  console.log(`[parasite] tick=${tick}`);
  r.log.forEach(l => console.log(`    ${l.event}  ${l.parasite}→${l.host}  ${l.bite != null ? "bite="+l.bite : "str="+l.hostStr}`));
  return r;
}
module.exports = { feed, cycle };
if (require.main === module) { console.log("METRIC PARASITE…\n"); for (let t = 0; t < 5; t++) cycle(t); }
