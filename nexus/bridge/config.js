const fs = require("fs");
const path = require("path");
const DEFAULTS = {
  version: "9.0.0-nexus", lineage_count: 28,
  interop: { metric_keys: ["strength", "entropy", "coherence", "consensus"], event_bus: "resonance_bus", threshold: { stabilize: 0.62, collapse: 0.28, overload: 0.85 } },
  bridge: { max_concurrent: 5, cycle_ticks: 2, exec_subset: 8 },
  watch: { interval_ms: 15000, max_cycles: 10 },
  journal: { enabled: true, max_entries: 100 }
};
function load() {
  try {
    const raw = JSON.parse(fs.readFileSync(path.join(__dirname, "../nexus.config"), "utf8"));
    return { ...DEFAULTS, ...raw,
      interop: { ...DEFAULTS.interop, ...(raw.interop || {}), threshold: { ...DEFAULTS.interop.threshold, ...(raw.interop?.threshold || {}) } },
      bridge: { ...DEFAULTS.bridge, ...(raw.bridge || {}) },
      watch: { ...DEFAULTS.watch, ...(raw.watch || {}) },
      journal: { ...DEFAULTS.journal, ...(raw.journal || {}) }
    };
  } catch (e) { return { ...DEFAULTS }; }
}
function thresholds() { return load().interop.threshold; }
module.exports = { load, thresholds, DEFAULTS };
