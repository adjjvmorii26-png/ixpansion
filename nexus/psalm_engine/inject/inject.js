const fs = require("fs");
const path = require("path");
const { generate } = require("../psalm.js");
const VOICES = path.join(__dirname, "../../meta_choir/choir_voices.stream");
const ECHO = path.join(__dirname, "../../meta_choir/choir_memory.echo");
function inject(metrics = {}, decision = null) {
  const psalm = generate(metrics, decision);
  const line = `${Date.now()} | ${psalm.agent} | ${psalm.line}\n`;
  try { fs.appendFileSync(VOICES, line); } catch (e) { try { fs.writeFileSync(VOICES, line); } catch (e2) {} }
  try { fs.writeFileSync(ECHO, `echo_id: NX-AUTO\nagent: ${psalm.agent}\nline: ${psalm.line}\nmetrics: ${JSON.stringify(psalm.metrics)}\ndecision: ${decision || "none"}\n`); } catch (e) {}
  console.log(`[inject] ${psalm.agent}: "${psalm.line}"`);
  return psalm;
}
function readVoices(n = 5) {
  try { return fs.readFileSync(VOICES, "utf8").trim().split("\n").slice(-n); } catch (e) { return []; }
}
function cycle(tick = 0) {
  const samples = [{ strength: 0.8, entropy: 0.2, consensus: 0.75 }, { strength: 0.4, entropy: 0.6, consensus: 0.3 }, { strength: 0.65, entropy: 0.35, consensus: 0.7 }];
  const m = samples[tick % samples.length];
  const decision = m.consensus < 0.35 ? "COLLAPSE" : "STABILIZE";
  const psalm = inject(m, decision);
  readVoices(3).forEach(l => console.log(`    ${l.slice(0, 80)}`));
  return psalm;
}
module.exports = { inject, readVoices, cycle };
if (require.main === module) { console.log("PSALM INJECT…\n"); for (let t = 0; t < 3; t++) cycle(t); }
