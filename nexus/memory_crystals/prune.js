const crystals = require("./crystal_store.js");
function prune({ keepHist = 12, dropHist = false } = {}) {
  const names = crystals.list();
  const hist = names.filter(n => n.startsWith("hist_")).sort();
  let removed = [];
  if (dropHist) hist.forEach(n => { crystals.purge(n); removed.push(n); });
  else if (hist.length > keepHist) {
    hist.slice(0, hist.length - keepHist).forEach(n => { crystals.purge(n); removed.push(n); });
  }
  const sum = crystals.summary();
  console.log(`[prune] removed ${removed.length}  remaining=${sum.count}`);
  return { removed: removed.length, remaining: sum.count };
}
module.exports = { prune };
if (require.main === module) {
  const drop = process.argv.includes("--all-hist");
  const keep = parseInt(process.argv.find(a => a.startsWith("--keep="))?.split("=")[1] || "12", 10);
  prune({ keepHist: keep, dropHist: drop });
  console.log("summary:", crystals.summary());
}
