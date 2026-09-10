const { publish } = require("../../resonance_bus/bus.js");
function dissent(nodes = [], threshold = 0.55) {
  const votes = nodes.map(n => ({ id: n.id, natural: n.strength >= threshold && (n.entropy ?? 0.3) < 0.55, strength: n.strength }));
  const dissenter = [...votes].sort((a, b) => a.strength - b.strength)[0];
  let yes = 0, no = 0, wYes = 0, wNo = 0;
  const final = votes.map(v => {
    const support = v.id === dissenter.id ? !v.natural : v.natural;
    if (support) { yes++; wYes += v.strength; } else { no++; wNo += v.strength; }
    return { ...v, support, dissented: v.id === dissenter.id };
  });
  const consensus = wYes / (wYes + wNo || 1);
  const decision = consensus >= 0.5 ? "STABILIZE" : "COLLAPSE";
  publish("DISSENT", { dissenter: dissenter.id, decision, consensus: +consensus.toFixed(3) });
  return { decision, consensus: +consensus.toFixed(3), yes, no, dissenter: dissenter.id, votes: final };
}
function cycle(tick = 0) {
  const nodes = [
    { id: "scribe", strength: 0.82, entropy: 0.2 },
    { id: "flux", strength: 0.7 - tick * 0.05, entropy: 0.3 },
    { id: "mirror", strength: 0.75, entropy: 0.25 },
    { id: "void", strength: 0.4 + tick * 0.03, entropy: 0.55 }
  ];
  const r = dissent(nodes, 0.55);
  console.log(`[dissent] tick=${tick}  dissenter=${r.dissenter}  decision=${r.decision}  consensus=${r.consensus}`);
  return r;
}
module.exports = { dissent, cycle };
if (require.main === module) { console.log("CHOIR DISSONANCE…\n"); for (let t = 0; t < 4; t++) cycle(t); }
