/** Shared IXpansion JS — the organism's client-side ontology.
 *
 * Single source of truth for wave, version, and narrative on the
 * dashboard side. Every dashboard includes this to render uniform
 * identity without hardcoding.
 */
window.IXP = {
  version: "4.02.0",
  wave: 214,
  waveName: "The Organism Immortalizes",
  narrativeArc: [
    "observe","heal","govern","feel","sing","move",
    "speak","feast","excavate","forecast","symbiose",
    "map-limits","develop-taste",
    "speak-itself",
  ],
  statusVocabulary: [
    "resonant","coherent","drifting","fracturing",
    "dormant","stable","thriving","fragile",
  ],

  /** Render the canonical identity badge into an element. */
  renderIdentity: function (el) {
    if (!el) return;
    el.textContent = "Wave " + this.wave + " · v" + this.version + " · " + this.waveName;
  },

  /** Return the canonical status for a raw value. */
  canonicalStatus: function (raw) {
    const s = String(raw || "").toLowerCase().trim();
    const aliases = {
      "healthy":"resonant","good":"resonant","active":"stable","ok":"stable",
      "alive":"stable","pass":"stable","degraded":"drifting","warning":"drifting",
      "error":"fracturing","broken":"fracturing","down":"fracturing",
      "unsettled":"drifting","crisis":"fracturing","elite":"thriving",
    };
    if (this.statusVocabulary.includes(s)) return s;
    return aliases[s] || "stable";
  },

  /** Load live identity from the ontology endpoint (falls back to constants). */
  async loadLive: function (cb) {
    try {
      const r = await fetch("/api/organism_ontology");
      const d = await r.json();
      if (d.version) this.version = d.version;
      if (d.wave) this.wave = d.wave;
      if (d.wave_name) this.waveName = d.wave_name;
      if (cb) cb(d);
    } catch (e) {
      if (cb) cb(null);
    }
  }
};
