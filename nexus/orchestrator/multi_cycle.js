const { run } = require("./run_cycle.js");
const { latest } = require("../reports/report.js");
const crystals = require("../memory_crystals/crystal_store.js");
function multi(n = 2) {
  console.log(`MULTI-CYCLE × ${n}\n`);
  const trail = [];
  for (let i = 0; i < n; i++) {
    console.log(`\n======== cycle ${i + 1}/${n} ========\n`);
    const result = run(1);
    trail.push({
      i: i + 1,
      decision: result.mesh?.decision,
      consensus: result.mesh?.consensus,
      oracle: result.oracle?.name,
      crystals: result.crystals?.count,
      avgStrength: result.crystals?.avgStrength,
      execOk: result.exec?.ok
    });
  }
  console.log("\nTRAIL SUMMARY");
  trail.forEach(t => {
    console.log(`  #${t.i}  ${t.decision || "?"}  c=${t.consensus ?? "?"}  oracle=${t.oracle || "?"}  crystals=${t.crystals}`);
  });
  const sum = crystals.summary();
  console.log(`\nfinal crystals: ${sum.count}  avg_str=${sum.avgStrength}`);
  const rep = latest();
  if (rep) console.log(`latest report: ${rep.id}`);
  console.log();
  return trail;
}
module.exports = { multi };
if (require.main === module) multi(parseInt(process.argv[2] || "2", 10));
