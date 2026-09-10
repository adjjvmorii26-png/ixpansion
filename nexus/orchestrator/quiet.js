const { spawnSync } = require("child_process");
const path = require("path");
const { latest } = require("../reports/report.js");
const crystals = require("../memory_crystals/crystal_store.js");
const { load: loadExport } = require("../metrics_export/export.js");
function quiet() {
  const result = spawnSync("node", [path.join(__dirname, "run_cycle.js")], {
    encoding: "utf8",
    env: { ...process.env, NODE_NO_WARNINGS: "1" },
    timeout: 60000
  });
  const out = (result.stdout || "") + (result.stderr || "");
  const pick = (re) => { const m = out.match(re); return m ? m[0] : null; };
  const execLine = pick(/\[exec\][^\n]+/);
  const oracleLine = pick(/\w+_WIND|\w+_FACE|\w+_BLOOM|\w+_GIFT/);
  const reportLine = pick(/\[report\] wrote[^\n]+/);
  const rep = latest();
  const sum = crystals.summary();
  const frame = loadExport();
  console.log("══════════════════════════════════════");
  console.log("  NEXUS QUIET CYCLE");
  console.log("══════════════════════════════════════");
  if (execLine) console.log(" ", execLine);
  if (oracleLine) console.log("  oracle:", oracleLine.trim());
  if (rep?.mesh) console.log(`  mesh: ${rep.mesh.decision} @ ${rep.mesh.consensus}`);
  if (rep?.psalm) console.log(`  psalm: ${rep.psalm.agent} — "${rep.psalm.line}"`);
  console.log(`  crystals: ${sum.count}  avg_str=${sum.avgStrength}  avg_ent=${sum.avgEntropy}`);
  if (frame?.systems) console.log(`  export: ${frame.systems.length} systems`);
  if (reportLine) console.log(" ", reportLine);
  if (result.status !== 0) console.log("  exit:", result.status);
  console.log("══════════════════════════════════════\n");
  return { status: result.status, report: rep, crystals: sum };
}
module.exports = { quiet };
if (require.main === module) quiet();
