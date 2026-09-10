const fs = require("fs");
const path = require("path");
const STORE_PATH = path.join(__dirname, "store.json");
let mem = { crystals: {}, version: 1, updated: null };
function load() {
  try { if (fs.existsSync(STORE_PATH)) mem = JSON.parse(fs.readFileSync(STORE_PATH, "utf8")); } catch (e) {}
  return mem;
}
function save(data) {
  data.updated = new Date().toISOString();
  mem = data;
  try { fs.writeFileSync(STORE_PATH, JSON.stringify(data, null, 2)); } catch (e) {}
  return data;
}
function seal(name, metrics = {}, payload = {}) {
  const data = load();
  data.crystals[name] = {
    name,
    metrics: {
      strength: +(metrics.strength ?? 0.5).toFixed(4),
      entropy: +(metrics.entropy ?? 0.3).toFixed(4),
      coherence: +(metrics.coherence ?? 0.6).toFixed(4),
      consensus: +(metrics.consensus ?? 0.5).toFixed(4)
    },
    payload,
    sealed_at: new Date().toISOString(),
    cycle: (data.crystals[name]?.cycle || 0) + 1
  };
  save(data);
  return data.crystals[name];
}
function recall(name) { return load().crystals[name] || null; }
function list() { return Object.keys(load().crystals); }
function decay(name, rate = 0.04) {
  const data = load();
  const c = data.crystals[name];
  if (!c) return null;
  c.metrics.strength = Math.max(0, +(c.metrics.strength - rate).toFixed(4));
  c.metrics.entropy = Math.min(1, +(c.metrics.entropy + rate * 0.8).toFixed(4));
  c.metrics.coherence = Math.max(0, +(c.metrics.coherence - rate * 0.5).toFixed(4));
  c.decayed_at = new Date().toISOString();
  save(data);
  return c;
}
function purge(name) { const data = load(); delete data.crystals[name]; save(data); }
function summary() {
  const data = load();
  const names = Object.keys(data.crystals);
  if (!names.length) return { count: 0, avgStrength: 0, avgEntropy: 0, names: [] };
  let s = 0, e = 0;
  names.forEach(n => { s += data.crystals[n].metrics.strength; e += data.crystals[n].metrics.entropy; });
  return { count: names.length, avgStrength: +(s / names.length).toFixed(3), avgEntropy: +(e / names.length).toFixed(3), names };
}
module.exports = { seal, recall, list, decay, purge, summary, load };
