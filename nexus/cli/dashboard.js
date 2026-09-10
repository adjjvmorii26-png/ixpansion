const crystals = require("../memory_crystals/crystal_store.js");
const { latest } = require("../reports/report.js");
const { load: loadExport } = require("../metrics_export/export.js");
const lineage = require("../lineage_map/map.js");
const { available } = require("../bridge/exec_adapters/exec.js");
const { recent } = require("../resonance_bus/bus.js");
function bar(n, w = 10) {
  const f = Math.round(Math.max(0, Math.min(1, n)) * w);
  return "█".repeat(f) + "░".repeat(w - f);
}
function dashboard() {
  console.log("NEXUS DASHBOARD\n");
  console.log(`Lineage systems : ${lineage.count()}`);
  console.log(`Exec available  : ${available().length}`);
  console.log(`Themes          : ${lineage.themes().join(", ")}\n`);
  const sum = crystals.summary();
  console.log("▸ Memory Crystals");
  console.log(`  count=${sum.count}  avg_str=${sum.avgStrength}  avg_ent=${sum.avgEntropy}`);
  (sum.names || []).slice(0, 6).forEach(n => {
    const c = crystals.recall(n);
    if (c) console.log(`  ${n.padEnd(28)} str=${c.metrics.strength} ent=${c.metrics.entropy}`);
  });
  if ((sum.names || []).length > 6) console.log(`  … +${sum.names.length - 6} more`);
  console.log("\n▸ Latest Report");
  const rep = latest();
  if (rep) {
    console.log(`  id=${rep.id}  sealed=${rep.sealed_at}`);
    if (rep.mesh) console.log(`  mesh: ${rep.mesh.decision} @ ${rep.mesh.consensus}`);
    if (rep.oracle) console.log(`  oracle: ${rep.oracle.name}`);
    if (rep.psalm) console.log(`  psalm: ${rep.psalm.agent} — "${rep.psalm.line}"`);
    if (rep.exec) console.log(`  exec: ${rep.exec.ok}/${rep.exec.total} avgS=${rep.exec.avgStrength}`);
  } else console.log("  (no reports yet)");
  console.log("\n▸ Metrics Export");
  const frame = loadExport();
  if (frame?.systems?.length) {
    console.log(`  systems=${frame.systems.length}`);
    frame.systems.slice(0, 6).forEach(s => console.log(`  ${String(s.label).padEnd(26)} ${bar(s.metrics.strength)} ${s.metrics.strength}`));
  } else console.log("  (no export yet)");
  console.log("\n▸ Resonance Bus");
  const bus = recent(5);
  if (bus.length) bus.forEach(e => console.log(`  ${e.event}`));
  else console.log("  (empty — process-local)");
  console.log();
}
module.exports = { dashboard };
if (require.main === module) dashboard();
