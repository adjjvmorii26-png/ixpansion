const fs = require("fs");
const path = require("path");
const LOG = path.join(__dirname, "journal.jsonl");
const MD = path.join(__dirname, "JOURNAL.md");
function append(entry = {}) {
  const row = { t: new Date().toISOString(), id: entry.id || `j_${Date.now().toString(36)}`, decision: entry.decision || null, consensus: entry.consensus ?? null, oracle: entry.oracle || null, psalm: entry.psalm || null, exec_ok: entry.exec_ok ?? null, crystals: entry.crystals ?? null };
  try { fs.appendFileSync(LOG, JSON.stringify(row) + "\n"); } catch (e) {}
  try {
    const lines = fs.existsSync(LOG) ? fs.readFileSync(LOG, "utf8").trim().split("\n") : [];
    const md = ["# Nexus Journal", "", ...lines.slice(-50).map(l => { try { const e = JSON.parse(l); return `- **${e.t}** · ${e.decision} @ ${e.consensus} · ${e.oracle}`;} catch (err) { return ""; } }), ""].join("\n");
    fs.writeFileSync(MD, md);
  } catch (e) {}
  return row;
}
function recent(n = 10) {
  try { return fs.readFileSync(LOG, "utf8").trim().split("\n").filter(Boolean).slice(-n).map(l => JSON.parse(l)); }
  catch (e) { return []; }
}
module.exports = { append, recent, LOG, MD };
