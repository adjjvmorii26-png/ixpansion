const fs = require("fs");
const path = require("path");
const { recent, publish } = require("./bus.js");
const STORE = path.join(__dirname, "reliquary.jsonl");
function seal(n = 20) {
  const events = recent(n);
  try { events.forEach(e => fs.appendFileSync(STORE, JSON.stringify(e) + "\n")); } catch (err) {}
  return events.length;
}
function loadTail(n = 15) {
  try {
    return fs.readFileSync(STORE, "utf8").trim().split("\n").filter(Boolean).slice(-n).map(l => {
      try { return JSON.parse(l); } catch (e) { return { raw: l }; }
    });
  } catch (e) { return []; }
}
function cycle() {
  publish("RELIQUARY_TICK", { t: Date.now() });
  const n = seal(10);
  const tail = loadTail(5);
  console.log(`[reliquary] sealed ${n}  tail=${tail.length}`);
  tail.forEach(e => console.log(`  ${e.event || "?"} ${JSON.stringify(e.payload || {}).slice(0, 40)}`));
  return { sealed: n, tail };
}
module.exports = { seal, loadTail, cycle, STORE };
if (require.main === module) cycle();
