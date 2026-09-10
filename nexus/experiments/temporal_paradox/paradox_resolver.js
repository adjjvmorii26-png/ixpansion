const { publish } = require("../../resonance_bus/bus.js");
function claim(timeline, assertion, weight = 0.5) {
  return { timeline, assertion, weight };
}
function detect(claims = []) {
  const byAssertion = {};
  claims.forEach(c => {
    if (!byAssertion[c.assertion]) byAssertion[c.assertion] = [];
    byAssertion[c.assertion].push(c);
  });
  const paradoxes = [];
  const tags = Object.keys(byAssertion);
  if (tags.includes("stable") && tags.includes("collapsed"))
    paradoxes.push({ type: "stable_vs_collapsed", claims: [...byAssertion.stable, ...byAssertion.collapsed] });
  if (tags.includes("open") && tags.includes("sealed"))
    paradoxes.push({ type: "open_vs_sealed", claims: [...byAssertion.open, ...byAssertion.sealed] });
  return paradoxes;
}
function suture(paradox, force = 0.7) {
  const winner = paradox.claims.reduce((a, b) => a.weight >= b.weight ? a : b);
  const residual = 1 - force;
  publish("PARADOX_SUTURE", { type: paradox.type, winner: winner.timeline, force });
  return { resolved: true, dominant: winner.timeline, assertion: winner.assertion, residualEntropy: +(residual * 0.4).toFixed(3) };
}
function cycle(tick = 0) {
  const claims = [
    claim("alpha", "stable", 0.7 + tick * 0.02),
    claim("beta", "collapsed", 0.55),
    claim("delta", "stable", 0.4),
    claim("gamma", tick % 2 === 0 ? "open" : "sealed", 0.6)
  ];
  const paradoxes = detect(claims);
  const resolutions = paradoxes.map(p => suture(p, 0.65 + tick * 0.02));
  console.log(`[paradox] tick=${tick}  detected=${paradoxes.length}  resolved=${resolutions.length}`);
  return { detected: paradoxes.length, resolved: resolutions.length, resolutions };
}
module.exports = { claim, detect, suture, cycle };
if (require.main === module) { console.log("TEMPORAL PARADOX…\n"); for (let t = 0; t < 5; t++) cycle(t); }
