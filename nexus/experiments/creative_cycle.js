const mods = [
  ["Dream Buffer", "./dream_buffer/dream_buffer.js"],
  ["Symbiosis", "./symbiosis/symbiosis.js"],
  ["Echo Archaeology", "./echo_archaeology/archaeology.js"],
  ["Oracle Die", "./oracle_die/oracle.js"],
  ["Entropy Garden", "./entropy_garden/garden.js"],
  ["Tide Clock", "./tide_clock/tide.js"],
  ["Collapse Compost", "./collapse_compost/compost.js"],
  ["Liminal Gate", "./liminal_gate/gate.js"],
  ["Choir Dissonance", "./choir_dissonance/dissonance.js"],
  ["Palimpsest", "./palimpsest/palimpsest.js"],
  ["Mirror Twin", "./mirror_twin/mirror.js"],
  ["Resonance Chord", "./resonance_chord/chord.js"],
  ["Gravity Well", "./gravity_well/gravity.js"],
  ["Cascade Fail", "./cascade_fail/cascade.js"],
  ["Chrono Bookmark", "./chrono_bookmark/bookmark.js"],
  ["Faction Swarm", "./faction_swarm/swarm.js"],
  ["Entropy Diffraction", "./entropy_diffraction/diffraction.js"],
  ["Coherence Lattice", "./coherence_lattice/lattice.js"],
  ["Null Baptism", "./null_baptism/baptism.js"],
  ["Echo Ledger", "./echo_ledger/ledger.js"],
  ["Phase Lock Choir", "./phase_lock_choir/choir.js"],
  ["Metric Parasite", "./metric_parasite/parasite.js"],
  ["Temporal Fold", "./temporal_fold/fold.js"],
  ["Consensus Fog", "./consensus_fog/fog.js"],
  ["Sigil Anchor", "./sigil_anchor/anchor.js"],
  ["Harmonic Interference", "./harmonic_interference/interfere.js"]
];
function run(ticks = 2) {
  console.log("CREATIVE EXPERIMENTS (Wave 12)\n");
  for (const [label, rel] of mods) {
    console.log(`▸ ${label}`);
    try {
      const mod = require(rel);
      if (label === "Liminal Gate" && mod.reset) mod.reset();
      if (label === "Null Baptism" && mod.state) mod.state.clear();
      if (label === "Temporal Fold" && mod.past) mod.past.clear();
      if (label === "Sigil Anchor" && mod.sigils) mod.sigils.clear();
      for (let t = 0; t < ticks; t++) mod.cycle(t);
    } catch (e) { console.log(`  FAIL: ${e.message}`); }
    console.log();
  }
  try { console.log("▸ Myth Weaver"); require("./myth_weaver/myth.js").cycle(0); console.log(); } catch (e) {}
  try { console.log("▸ Signal Reliquary"); require("../resonance_bus/reliquary.js").cycle(); console.log(); } catch (e) {}
  console.log("Creative cycle complete.\n");
}
module.exports = { run };
if (require.main === module) run(2);
