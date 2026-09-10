const { publish } = require("../../resonance_bus/bus.js");
const books = [];
function entry(from, to, metric, amount, note = "") {
  const row = { t: Date.now(), from, to, metric, amount: +(+amount).toFixed(4), note };
  books.push(row);
  if (books.length > 200) books.shift();
  return row;
}
function balance(metric = "coherence") {
  const scores = {};
  books.filter(b => b.metric === metric).forEach(b => {
    scores[b.from] = (scores[b.from] || 0) - b.amount;
    scores[b.to] = (scores[b.to] || 0) + b.amount;
  });
  const sum = Object.values(scores).reduce((a, v) => a + v, 0);
  if (Math.abs(sum) > 0.001) publish("LEDGER_DRIFT", { metric, sum: +sum.toFixed(4) });
  else publish("LEDGER_OK", { metric, entries: books.length });
  return { scores, sum: +sum.toFixed(4), entries: books.length };
}
function cycle(tick = 0) {
  entry("void", "attention", "coherence", 0.03 + tick * 0.01, "gravity");
  entry("quietus", "attention", "coherence", 0.02, "gravity");
  if (tick === 2) entry("attention", "metamorph", "coherence", 0.04, "gift");
  const b = balance("coherence");
  console.log(`[ledger] tick=${tick}  entries=${b.entries}  sum=${b.sum}`);
  Object.entries(b.scores).forEach(([id, v]) => console.log(`    ${id}: ${v > 0 ? "+" : ""}${v.toFixed(4)}`));
  return b;
}
module.exports = { entry, balance, cycle, books };
if (require.main === module) { console.log("ECHO LEDGER…\n"); for (let t = 0; t < 4; t++) cycle(t); }
