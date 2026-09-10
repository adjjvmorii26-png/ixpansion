const { plant, apply, sigils } = require("../experiment/sigil_anchor/anchor.js");
const { remember, fold, past } = require("../experiment/temporal_fold/fold.js");
const { vote } = require("../experiment/consensus_fog/fog.js");
const { interfere } = require("../experiment/harmonic_interference/interfere.js");
const { feed } = require("../experiment/metric_parasite/parasite.js");
function run(raw = []) {
  let nodes = (raw.length ? raw : [
    { id: "gate", strength: 0.45, entropy: 0.4, coherence: 0.4, consensus: 0.48, phase: 0.2 },
    { id: "host", strength: 0.78, entropy: 0.25, coherence: 0.65, consensus: 0.6, phase: 0.22 },
    { id: "leech", strength: 0.32, entropy: 0.5, coherence: 0.3, consensus: 0.45, phase: 0.7 },
    { id: "mirror", strength: 0.66, entropy: 0.3, coherence: 0.55, consensus: 0.52, phase: 0.25 }
  ]).map(n => ({ ...n }));
  console.log("▸ Wave 12 Pass");
  nodes.forEach(n => remember(n.id, n));
  if (!sigils.has("wave12_seal")) plant("wave12_seal", "gate", { strength: 0.8, coherence: 0.75 }, 3);
  let r = apply(nodes);
  console.log(`  sigil active=${r.active.length}`);
  nodes = r.nodes;
  r = fold(nodes, 0.55);
  console.log(`  fold alpha=${r.alpha}`);
  nodes = r.nodes;
  const fog = vote(nodes, 11);
  console.log(`  fog ${fog.decision} @ ${fog.consensus} fogged=${fog.fogged}`);
  const sources = nodes.slice(0, 2).map(n => ({ id: n.id, phase: n.phase ?? n.consensus ?? 0.5, amplitude: 0.07 }));
  r = interfere(nodes, sources);
  console.log(`  interfere +${r.constructive}/-${r.destructive}`);
  nodes = r.nodes;
  r = feed(nodes, [{ parasite: "leech", host: "host" }], 0.05);
  console.log(`  parasite events=${r.log.length}\n`);
  return { nodes, fog, sigils: [...sigils.keys()] };
}
module.exports = { run };
if (require.main === module) { sigils.clear(); past.clear(); run(); }
