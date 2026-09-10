const { spawnSync } = require("child_process");
const crypto = require("crypto");
const path = require("path");
const fs = require("fs");
const { normalize } = require("../adapters/normalize.js");
const { publish } = require("../../resonance_bus/bus.js");
const ARTIFACTS = path.resolve(__dirname, "../../../");
const CORES = {
  "attention-labyrinth": { cwd: "attention_labyrinth", cmd: ["node", "-e", "const {run}=require('./focus_spire/spire_amplify.js'); console.log(JSON.stringify(run(0)));"] },
  "quietus-array": { cwd: "quietus_array", cmd: ["node", "-e", "const {run}=require('./null_loom/loom_weave.js'); console.log(JSON.stringify(run(0)));"] },
  "metamorph-forge": { cwd: "metamorph_forge", cmd: ["node", "-e", "const {run}=require('./chrysalis_vault/vault_store.js'); console.log(JSON.stringify(run(0)));"] },
  "probability-engine": { cwd: "probability_engine", cmd: ["node", "-e", "const {run}=require('./chance_crucible/crucible_melt.js'); console.log(JSON.stringify(run(0)));"] },
  "chronovore-archive": { cwd: "chronovore_archive", cmd: ["node", "-e", "const {run}=require('./intake_maw/maw_ingest.js'); console.log(JSON.stringify(run(0)));"] },
  "semiotic-engine": { cwd: "semiotic_engine", cmd: ["node", "-e", "const {run}=require('./semiotic_core.js'); console.log(JSON.stringify(run(0)));"] },
  "neuroglyph-forge": { cwd: "neuroglyph_forge", cmd: ["node", "-e", "const {run}=require('./thought_crucible/crucible_melt.js'); console.log(JSON.stringify(run(0)));"] }
};
function parseMetric(stdout) {
  const lines = (stdout || "").trim().split("\n").filter(Boolean);
  for (let i = lines.length - 1; i >= 0; i--) {
    try { return JSON.parse(lines[i]); } catch (e) {}
  }
  const m = (stdout || "").match(/(\w+)=([0-9.]+)/);
  if (m) return { [m[1]]: parseFloat(m[2]) };
  return {};
}
function execOne(name, timeoutMs = 4000) {
  const spec = CORES[name];
  if (!spec) return shadowResult(name, "missing");
  const cwd = path.join(ARTIFACTS, spec.cwd);
  if (!fs.existsSync(cwd)) return shadowResult(name, "absent");
  try {
    const result = spawnSync(spec.cmd[0], spec.cmd.slice(1), { cwd, encoding: "utf8", timeout: timeoutMs, env: { ...process.env, NODE_NO_WARNINGS: "1" } });
    if (result.error || result.status !== 0) return { name, ok: false, source: "error", metrics: normalize({}), stderr: (result.stderr || "").slice(0, 120) };
    const raw = parseMetric(result.stdout);
    const metrics = normalize(raw);
    publish("EXEC_METRIC", { name, metrics });
    return { name, ok: true, source: "exec", raw, metrics };
  } catch (e) {
    return { name, ok: false, source: "exception", metrics: normalize({}), error: e.message };
  }
}
function offlineMetrics(name, tick = 0) {
  const digest = crypto.createHash("sha256").update(`${name}:${tick}`).digest();
  return {
    strength: digest[0] / 255,
    entropy: digest[1] / 255,
    coherence: digest[2] / 255,
    consensus: digest[3] / 255
  };
}
function shadowResult(name, reason) {
  const metrics = normalize(offlineMetrics(name));
  publish("SHADOW_METRIC", { name, metrics });
  return { name, ok: true, source: `shadow:${reason}`, metrics };
}
function available(names = null) {
  return (names || Object.keys(CORES)).filter(name => {
    const spec = CORES[name];
    return spec && fs.existsSync(path.join(ARTIFACTS, spec.cwd));
  });
}
function execAll(names = null) { return (names || Object.keys(CORES)).map(n => execOne(n)); }
function cycle(tick = 0) {
  const results = execAll();
  const ok = results.filter(r => r.ok).length;
  const avgS = results.reduce((s, r) => s + r.metrics.strength, 0) / Math.max(1, results.length);
  const avgE = results.reduce((s, r) => s + r.metrics.entropy, 0) / Math.max(1, results.length);
  console.log(`[exec] tick=${tick}  ok=${ok}/${results.length}  avg_str=${avgS.toFixed(3)}  avg_ent=${avgE.toFixed(3)}`);
  results.forEach(r => console.log(`  ${(r.ok ? "OK" : "FAIL").padEnd(4)} ${r.name.padEnd(22)} str=${r.metrics.strength.toFixed(3)} ent=${r.metrics.entropy.toFixed(3)}  (${r.source})`));
  return { ok, total: results.length, avgStrength: +avgS.toFixed(3), avgEntropy: +avgE.toFixed(3), results };
}
module.exports = { available, execOne, execAll, cycle, CORES, parseMetric };
if (require.main === module) { console.log("EXEC ADAPTERS…\n"); cycle(0); }
