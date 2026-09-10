const { execAll } = require("../bridge/exec_adapters/exec.js");
const { normalize, clamp } = require("../bridge/adapters/normalize.js");
const lineage = require("../lineage_map/map.js");
const REQUIRED_KEYS = ["strength", "entropy", "coherence", "consensus"];
function assertShape(metrics, name) {
  const errors = [];
  REQUIRED_KEYS.forEach(k => {
    if (typeof metrics[k] !== "number" || Number.isNaN(metrics[k])) errors.push(`${name}: missing/NaN ${k}`);
    else if (metrics[k] < 0 || metrics[k] > 1) errors.push(`${name}: ${k}=${metrics[k]} out of [0,1]`);
  });
  return errors;
}
function smoke(name, fn) {
  try { fn(); console.log(`  PASS  ${name}`); return []; }
  catch (e) { console.log(`  FAIL  ${name} — ${e.message}`); return [`${name}: ${e.message}`]; }
}
function run() {
  console.log("NEXUS CI — Wave 10\n");
  let failures = [], passes = 0;
  const results = execAll(["attention-labyrinth", "quietus-array", "metamorph-forge", "chronovore-archive", "neuroglyph-forge", "semiotic-engine"]);
  console.log("▸ Exec shape");
  results.forEach(r => {
    const errs = assertShape(r.metrics, r.name);
    if (!r.ok) errs.push(`${r.name}: exec failed`);
    if (errs.length) { failures = failures.concat(errs); console.log(`  FAIL  ${r.name}`); }
    else { passes++; console.log(`  PASS  ${r.name}`); }
  });
  if (normalize({ strength: 0.5 }).strength !== 0.5) failures.push("normalize");
  if (clamp(2) !== 1) failures.push("clamp");
  console.log("\n▸ Creative smoke");
  [
    ["dream", () => require("../experiment/dream_buffer/dream_buffer.js").cycle(0)],
    ["oracle", () => require("../experiment/oracle_die/oracle.js").cycle(0)],
    ["gravity", () => require("../experiment/gravity_well/gravity.js").cycle(0)],
    ["cascade", () => require("../experiment/cascade_fail/cascade.js").cycle(0)],
    ["bookmark", () => require("../experiment/chrono_bookmark/bookmark.js").cycle(0)],
    ["swarm", () => require("../experiment/faction_swarm/swarm.js").cycle(0)],
    ["wave9_pass", () => require("../orchestrator/wave9_pass.js").run([
      { name: "a", metrics: { strength: 0.7, entropy: 0.2, coherence: 0.6, consensus: 0.5 }, theme: "cognitive" },
      { name: "b", metrics: { strength: 0.3, entropy: 0.7, coherence: 0.3, consensus: 0.3 }, theme: "ontological" }
    ])]
  ].forEach(([n, fn]) => { failures = failures.concat(smoke(n, fn)); });
  console.log(`\n  exec ${passes}/${results.length}  failures=${failures.length}`);
  if (failures.length) { console.log("\nCI FAILED"); process.exitCode = 1; }
  else console.log("\nCI PASSED");
}
module.exports = { run, assertShape };
if (require.main === module) run();
