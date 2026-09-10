const crystals = require("../memory_crystals/crystal_store.js");
const { load: loadExport } = require("../metrics_export/export.js");
const lineage = require("../lineage_map/map.js");
function aggregate() {
  const byTheme = {};
  const data = crystals.load();
  Object.values(data.crystals || {}).forEach(c => {
    const theme = c.payload?.theme || (c.name?.startsWith("hist_") ? c.name.split("_")[1] : null);
    if (!theme || theme === "default") return;
    if (!byTheme[theme]) byTheme[theme] = [];
    byTheme[theme].push(c.metrics);
  });
  console.log("THEME AGGREGATE\n");
  console.log("Themes:", lineage.themes().join(", "), "\n");
  Object.keys(byTheme).sort().forEach(theme => {
    const samples = byTheme[theme];
    const n = samples.length;
    const avg = (k) => samples.reduce((s, m) => s + (m[k] || 0), 0) / n;
    console.log(`▸ ${theme}  (n=${n})`);
    console.log(`    str=${avg("strength").toFixed(3)}  ent=${avg("entropy").toFixed(3)}  coh=${avg("coherence").toFixed(3)}`);
  });
  const frame = loadExport();
  if (frame?.systems?.length) {
    console.log("\n▸ Live export by theme");
    const live = {};
    frame.systems.forEach(s => {
      const t = s.theme || "unknown";
      if (!live[t]) live[t] = [];
      live[t].push(s.metrics);
    });
    Object.keys(live).sort().forEach(t => {
      const samples = live[t];
      const avgS = samples.reduce((s, m) => s + m.strength, 0) / samples.length;
      console.log(`    ${t.padEnd(14)} n=${samples.length}  avg_str=${avgS.toFixed(3)}`);
    });
  }
  console.log();
}
module.exports = { aggregate };
if (require.main === module) aggregate();
