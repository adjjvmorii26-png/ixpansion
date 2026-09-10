const { load: loadConfig } = require("../bridge/config.js");
const { quiet } = require("./quiet.js");
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
async function watch(opts = {}) {
  const cfg = loadConfig();
  const interval = opts.interval_ms ?? cfg.watch?.interval_ms ?? 15000;
  const max = opts.max_cycles ?? cfg.watch?.max_cycles ?? 5;
  console.log(`NEXUS WATCH  interval=${interval}ms  max=${max}\n`);
  for (let i = 0; i < max; i++) {
    console.log(`── watch cycle ${i + 1}/${max} ──`);
    try { quiet(); } catch (e) { console.log("  watch error:", e.message); }
    if (i < max - 1) { console.log(`  sleeping ${interval}ms…\n`); await sleep(interval); }
  }
  console.log("Watch complete.\n");
}
module.exports = { watch };
if (require.main === module) {
  watch({ max_cycles: parseInt(process.argv[2] || "3", 10), interval_ms: parseInt(process.argv[3] || "5000", 10) });
}
