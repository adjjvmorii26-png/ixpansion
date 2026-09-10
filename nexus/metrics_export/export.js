const fs = require("fs");
const path = require("path");
const OUT = path.join(__dirname, "latest.json");
function exportFrame(systems = [], meta = {}) {
  const frame = {
    t: Date.now(),
    meta: { wave: meta.wave || "5-report", decision: meta.decision || null, oracle: meta.oracle || null, consensus: meta.consensus ?? null },
    systems: systems.map(s => ({
      label: s.label || s.name || "sys",
      metrics: {
        strength: +(s.metrics?.strength ?? s.strength ?? 0.5).toFixed(3),
        entropy: +(s.metrics?.entropy ?? s.entropy ?? 0.3).toFixed(3),
        coherence: +(s.metrics?.coherence ?? s.coherence ?? 0.6).toFixed(3),
        consensus: +(s.metrics?.consensus ?? s.consensus ?? 0.5).toFixed(3)
      },
      theme: s.theme || null
    }))
  };
  try { fs.writeFileSync(OUT, JSON.stringify(frame, null, 2)); console.log(`[export] ${OUT} (${frame.systems.length} systems)`); }
  catch (e) { console.log(`[export] in-memory only (${frame.systems.length} systems)`); }
  return frame;
}
function load() { try { return JSON.parse(fs.readFileSync(OUT, "utf8")); } catch (e) { return null; } }
module.exports = { exportFrame, load, OUT };
