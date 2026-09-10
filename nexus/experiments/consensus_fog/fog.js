const { publish } = require("../../resonance_bus/bus.js");
function vote(nodes = [], seed = 0) {
  function noise(id, s) {
    let h = s * 2654435761;
    for (let i = 0; i < id.length; i++) h = (h ^ id.charCodeAt(i)) * 1597334677;
    return ((h >>> 0) % 1000) / 1000;
  }
  const votes = nodes.map(n => {
    const base = (n.strength >= 0.55 && (n.entropy ?? 0.3) < 0.55) ? 1 : 0;
    const conf = Math.abs((n.consensus ?? 0.5) - 0.5) * 2;
    const fog = 1 - conf;
    const flip = noise(n.id, seed) < fog * 0.45;
    const lean = flip ? 1 - base : base;
    return { id: n.id, lean: lean === 1 ? "STABILIZE" : "COLLAPSE", weight: n.strength ?? 0.5, fog: +fog.toFixed(3), flipped: flip };
  });
  let wS = 0, wC = 0;
  votes.forEach(v => { if (v.lean === "STABILIZE") wS += v.weight; else wC += v.weight; });
  const consensus = +(wS / (wS + wC || 1)).toFixed(3);
  const decision = consensus >= 0.5 ? "STABILIZE" : "COLLAPSE";
  const fogged = votes.filter(v => v.flipped).length;
  publish("CONSENSUS_FOG", { decision, consensus, fogged });
  return { decision, consensus, votes, fogged };
}
function cycle(tick = 0) {
  const nodes = [
    { id: "scribe", strength: 0.72, entropy: 0.25, consensus: 0.48 + tick * 0.05 },
    { id: "flux", strength: 0.55, entropy: 0.45, consensus: 0.5 },
    { id: "void", strength: 0.4, entropy: 0.6, consensus: 0.42 },
    { id: "mirror", strength: 0.68, entropy: 0.3, consensus: 0.55 }
  ];
  const r = vote(nodes, tick + 7);
  console.log(`[fog] tick=${tick}  ${r.decision} @ ${r.consensus}  fogged=${r.fogged}`);
  r.votes.forEach(v => console.log(`    ${v.id} ${v.lean} fog=${v.fog}${v.flipped ? " FLIP" : ""}`));
  return r;
}
module.exports = { vote, cycle };
if (require.main === module) { console.log("CONSENSUS FOG…\n"); for (let t = 0; t < 4; t++) cycle(t); }
