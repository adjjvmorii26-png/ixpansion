const { publish } = require("../../resonance_bus/bus.js");
const { normalize } = require("../../bridge/adapters/normalize.js");
function node(id, metrics) { return { id, ...normalize(metrics) }; }
function vote(nodes = [], threshold = 0.5) {
  let yes = 0, no = 0, weightYes = 0, weightNo = 0;
  nodes.forEach(n => {
    const support = n.strength >= threshold && n.entropy < 0.55;
    if (support) { yes++; weightYes += n.strength; }
    else { no++; weightNo += n.strength; }
  });
  const totalW = weightYes + weightNo || 1;
  const consensus = weightYes / totalW;
  const decision = consensus >= 0.5 ? "STABILIZE" : "COLLAPSE";
  publish("MESH_VOTE", { decision, consensus, yes, no });
  return { decision, consensus: +consensus.toFixed(3), yes, no, weightYes: +weightYes.toFixed(3) };
}
function cycle(tick = 0) {
  const nodes = [
    node("chronovore", { strength: 0.71, entropy: 0.32 }),
    node("neuroglyph", { strength: 0.68, entropy: 0.41 }),
    node("attention", { strength: 0.74 - tick * 0.03, entropy: 0.28 + tick * 0.04 }),
    node("quietus", { strength: 0.45, entropy: 0.62 }),
    node("metamorph", { strength: 0.66, entropy: 0.37 })
  ];
  const result = vote(nodes, 0.55);
  console.log(`[mesh] tick=${tick}  decision=${result.decision}  consensus=${result.consensus}  yes=${result.yes}/no=${result.no}`);
  return result;
}
module.exports = { node, vote, cycle };
if (require.main === module) { console.log("CONSENSUS MESH…\n"); for (let t = 0; t < 5; t++) cycle(t); }
