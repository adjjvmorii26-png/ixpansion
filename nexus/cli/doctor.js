const fs = require("fs");
const path = require("path");
const crystals = require("../memory_crystals/crystal_store.js");
const { latest } = require("../reports/report.js");
const { listReports } = require("../reports/compare.js");
const { load: loadExport } = require("../metrics_export/export.js");
const { load: loadConfig } = require("../bridge/config.js");
const { available } = require("../bridge/exec_adapters/exec.js");
const lineage = require("../lineage_map/map.js");
const journal = require("../journal/journal.js");
const EXP_ROOT = path.join(__dirname, "../experiment");
function listExperiments() {
  const found = [];
  try {
    fs.readdirSync(EXP_ROOT, { withFileTypes: true }).forEach(d => {
      if (!d.isDirectory()) return;
      if (fs.readdirSync(path.join(EXP_ROOT, d.name)).some(f => f.endsWith(".js"))) found.push(d.name);
    });
  } catch (e) {}
  return found.sort();
}
function doctor() {
  const issues = [], notes = [];
  const cfg = loadConfig();
  console.log("NEXUS DOCTOR\n");
  console.log("▸ Core");
  console.log(`  version  ${cfg.version}`);
  console.log(`  lineage  ${lineage.count()}  exec ${available().length}`);
  if (lineage.count() < 20) issues.push("lineage sparse");
  const sum = crystals.summary();
  console.log("\n▸ Crystals");
  console.log(`  count=${sum.count}  avg_str=${sum.avgStrength}  avg_ent=${sum.avgEntropy}`);
  if (sum.count === 0) issues.push("no crystals — npm run seed");
  else if (sum.count > 80) notes.push("crystal backlog — npm run prune");
  const rep = latest();
  console.log("\n▸ Reports");
  console.log(`  latest=${rep?.id || "(none)"}  archive=${listReports().length}  export=${loadExport()?.systems?.length || 0}`);
  if (!rep) issues.push("no reports");
  const j = journal.recent(3);
  console.log("\n▸ Journal (recent)");
  j.forEach(e => console.log(`  ${e.decision} @ ${e.consensus}  ${e.oracle || ""}`));
  const exps = listExperiments();
  console.log(`\n▸ Experiments  ${exps.length} modules`);
  console.log("\n▸ Wave passes");
  ["wave9_pass.js", "wave11_pass.js", "wave12_pass.js", "unified_wave_pass.js"].forEach(f => {
    const ok = fs.existsSync(path.join(__dirname, "../orchestrator", f));
    console.log(`  ${ok ? "✓" : "✗"}  ${f}`);
    if (!ok) issues.push(`missing ${f}`);
  });
  console.log();
  notes.forEach(n => console.log("  note:", n));
  issues.forEach(i => console.log("  ✗", i));
  console.log(issues.length ? `DOCTOR: ${issues.length} issue(s)` : "DOCTOR: OK");
  if (issues.length) process.exitCode = 1;
  return { issues, notes, experiments: exps.length };
}
module.exports = { doctor, listExperiments };
if (require.main === module) doctor();
