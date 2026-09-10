const fs = require("fs");
const path = require("path");
const crystals = require("../memory_crystals/crystal_store.js");
const { latest } = require("../reports/report.js");
const { listReports } = require("../reports/compare.js");
const { load: loadExport } = require("./export.js");
const { load: loadConfig } = require("../bridge/config.js");
const { available } = require("../bridge/exec_adapters/exec.js");
const lineage = require("../lineage_map/map.js");
const journal = require("../journal/journal.js");
const OUT = path.join(__dirname, "status.json");
function build() {
  const cfg = loadConfig();
  const sum = crystals.summary();
  const rep = latest();
  const frame = loadExport();
  const status = {
    t: new Date().toISOString(),
    version: cfg.version,
    lineage: lineage.count(),
    exec_available: available().length,
    crystals: { count: sum.count, avgStrength: sum.avgStrength, avgEntropy: sum.avgEntropy },
    report: rep ? { id: rep.id, decision: rep.mesh?.decision, consensus: rep.mesh?.consensus, oracle: rep.oracle?.name, psalm: rep.psalm?.line } : null,
    reports_archived: listReports().length,
    export_systems: frame?.systems?.length || 0,
    journal_tail: journal.recent(5),
    thresholds: cfg.interop?.threshold || {}
  };
  try { fs.writeFileSync(OUT, JSON.stringify(status, null, 2)); console.log(`[status] ${OUT}`); } catch (e) { console.log("[status] in-memory only"); }
  return status;
}
module.exports = { build, OUT };
if (require.main === module) console.log(JSON.stringify(build(), null, 2).slice(0, 500));
