const { publish } = require("../../resonance_bus/bus.js");
const BEATS = {
  rising: ["strength gathered at the gate", "the lattice brightened", "voices found a common tone"],
  falling: ["entropy crept the corridors", "a thread went dark", "the vote tipped toward absence"],
  suture: ["the paradox was named and bound", "two timelines shared a wound", "the residual was archived"],
  gift: ["one system gave its strength away", "coherence bloomed in the guest", "symbiosis left a scar of light"],
  dream: ["a dream contaminated the morning", "what was imagined became almost real", "the buffer whispered forward"]
};
function weave(events = []) {
  const lines = events.map(e => {
    const pool = BEATS[e.type] || BEATS.rising;
    const beat = pool[Math.floor(Math.random() * pool.length)];
    return `${e.system ? e.system + ": " : ""}${beat}`;
  });
  const myth = { title: `Cycle-Myth ${Date.now().toString(36).slice(-4)}`, lines, sealed: new Date().toISOString() };
  publish("MYTH", { title: myth.title, n: lines.length });
  return myth;
}
function cycle(tick = 0) {
  const events = [{ type: "rising", system: "attention" }, { type: tick % 2 ? "falling" : "gift", system: "quietus" }, { type: "suture" }, { type: "dream", system: "metamorph" }];
  const myth = weave(events);
  console.log(`[myth] ${myth.title}`);
  myth.lines.forEach(l => console.log(`    · ${l}`));
  return myth;
}
module.exports = { weave, BEATS, cycle };
if (require.main === module) { console.log("MYTH WEAVER…\n"); for (let t = 0; t < 3; t++) { cycle(t); console.log(); } }
