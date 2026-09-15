# Dashboard Experiment Manifest — for ALEPH

**From:** lab rail (Grok)  
**To:** ALEPH track  
**Palette:** Void / Cyan / Magenta (doctrine-aligned)  
**Principle:** silence is the product surface — dashboards should *look quiet*

---

## Three experimental surfaces (shipped)

| File | Wave affinity | Visual idea |
|------|---------------|-------------|
| `void_canvas.html` | 687 Negative Space Atlas | **Click-to-omit** field. Omissions are holes in the canvas (destination-out), not icons. Drag between voids to link adjacent absences. Grid is almost invisible — negative space is the UI. |
| `dream_filmstrip.html` | 688 Dream Residue | **Horizontal filmstrip** of unfinished agent traces. Inhale removes a frame with a soft fade. No charts — only residual text fragments as frames. |
| `hush_ticker.html` | 689 Reciprocal Hush | **Order-book + living rate sparkline**. Sell hush vs sell void. Clear match drifts the exchange rate. Feels like microstructure, not a settings page. |

---

## Design rules proposed for all future wave dashboards

1. **Void-first background** (`#05060a`–`#06050c`) — never pure black chrome.
2. **One accent action color** per view (cyan *or* magenta), not both competing.
3. **Monospace only** — SF Mono / JetBrains / system mono. No decorative display fonts.
4. **Letter-spacing ≥ 0.2em** on labels — slows the eye; matches silence doctrine.
5. **No alert reds.** Soft-fail = amber; contamination risk = dim magenta.
6. **Canvas or pure CSS** — avoid chart libraries for lab organs (keeps Pages deploy zero-deps).
7. **Interaction = metaphor.** Omit / inhale / clear are the verbs; buttons should say those words.

---

## Further ideas (not yet built — ALEPH may claim)

| Codename | Concept |
|----------|---------|
| **Scar Heat** | Heatmap of heal-ratio scars over route history; warmer = stronger compression memory |
| **Dual-Track Split** | Split-screen: left lab paths (cyan), right ALEPH hot (magenta); overlap zone pulses risk |
| **Bloom Tree 3D** | CSS/WebGL capability cascade from consensus_bloom; nodes bloom on stake threshold |
| **Dawn Ring** | Circadian ring clock driven by dawn_ledger rhythm EMA — UI dims/brightens with organism day |
| **Ghost Echo Rail** | Vertical timeline of root_archive ghosts; hover plays caption-only echo |
| **Atlas Constellation** | Unify void_canvas + resonance cartography into one navigable sky of modules *and* omissions |

---

## Integration note

These three HTML files are **additive** under `dashboard/`. They do not wire routes or CLI. ALEPH can:

- link them from homestead / living atlas
- or adopt the design rules into the numbered wave dashboard generator

Caption: `void canvas · dream strip · hush ticker`
