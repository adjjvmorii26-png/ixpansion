const { publish } = require("../../resonance_bus/bus.js");
const ECHOES = [
  { source: "sensoria_03", text: "Gust pressure exceeded; scentfold sealed residue.", fragment: 0.42 },
  { source: "mesh", text: "Consensus collapsed; void agent held residual.", fragment: 0.55 },
  { source: "paradox", text: "Stable/collapsed suture incomplete; residual entropy sealed.", fragment: 0.38 },
  { source: "quietus", text: "Null loom threads thinned to absence.", fragment: 0.61 },
  { source: "metamorph", text: "Molt incomplete; hybrid reef held the shell.", fragment: 0.47 }
];
function excavate(echo) {
  const f = echo.fragment;
  const ghost = { strength: +(f * 0.7 + Math.random() * 0.15).toFixed(3), entropy: +(0.4 + (1 - f) * 0.35).toFixed(3), coherence: +(f * 0.6).toFixed(3), consensus: +(f * 0.5).toFixed(3), source: echo.source, text: echo.text };
  publish("EXCAVATE", { source: echo.source, strength: ghost.strength });
  return ghost;
}
function cycle(tick = 0) {
  const echo = ECHOES[tick % ECHOES.length];
  const ghost = excavate(echo);
  console.log(`[archaeology] tick=${tick}  ${echo.source}  ghost_str=${ghost.strength}  ent=${ghost.entropy}`);
  console.log(`    "${echo.text.slice(0, 60)}…"`);
  return ghost;
}
module.exports = { excavate, ECHOES, cycle };
if (require.main === module) { console.log("ECHO ARCHAEOLOGY…\n"); for (let t = 0; t < 5; t++) cycle(t); }
