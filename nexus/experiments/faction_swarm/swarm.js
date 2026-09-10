const { publish } = require("../../resonance_bus/bus.js");
function swarm(nodes = [], factions = {}) {
  const factionScore = {};
  Object.entries(factions).forEach(([fname, ids]) => {
    const members = nodes.filter(n => ids.includes(n.id));
    if (!members.length) return;
    const avgS = members.reduce((s, n) => s + n.strength, 0) / members.length;
    const avgE = members.reduce((s, n) => s + (n.entropy ?? 0.3), 0) / members.length;
    factionScore[fname] = { avgStrength: avgS, avgEntropy: avgE, lean: avgS >= 0.55 && avgE < 0.5 ? "STABILIZE" : "COLLAPSE" };
  });
  const votes = nodes.map(n => {
    let faction = null;
    for (const [fname, ids] of Object.entries(factions)) if (ids.includes(n.id)) { faction = fname; break; }
    const lean = faction && factionScore[faction] ? factionScore[faction].lean : ((n.strength >= 0.55 && (n.entropy ?? 0.3) < 0.5) ? "STABILIZE" : "COLLAPSE");
    return { id: n.id, faction, lean, weight: n.strength };
  });
  let wS = 0, wC = 0;
  votes.forEach(v => { if (v.lean === "STABILIZE") wS += v.weight; else wC += v.weight; });
  const consensus = wS / (wS + wC || 1);
  const decision = consensus >= 0.5 ? "STABILIZE" : "COLLAPSE";
  publish("SWARM", { decision, consensus: +consensus.toFixed(3), factions: Object.keys(factionScore).length });
  return { decision, consensus: +consensus.toFixed(3), votes, factionScore };
}
function cycle(tick = 0) {
  const nodes = [
    { id: "scribe", strength: 0.8, entropy: 0.2 },
    { id: "flux", strength: 0.7 - tick * 0.05, entropy: 0.3 },
    { id: "void", strength: 0.4, entropy: 0.6 },
    { id: "mirror", strength: 0.65, entropy: 0.35 },
    { id: "oracle", strength: 0.55 + tick * 0.03, entropy: 0.4 }
  ];
  const factions = { order: ["scribe", "mirror"], chaos: ["void", "flux"], liminal: ["oracle"] };
  const r = swarm(nodes, factions);
  console.log(`[swarm] tick=${tick}  ${r.decision}  consensus=${r.consensus}`);
  Object.entries(r.factionScore).forEach(([f, s]) => console.log(`    faction ${f}: lean=${s.lean} avgS=${s.avgStrength.toFixed(3)}`));
  return r;
}
module.exports = { swarm, cycle };
if (require.main === module) { console.log("FACTION SWARM…\n"); for (let t = 0; t < 4; t++) cycle(t); }
