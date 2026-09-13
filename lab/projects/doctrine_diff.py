#!/usr/bin/env python3
"""Doctrine Diff — sacred phrases vs repo text (drift map + captions)."""
from __future__ import annotations
import json, hashlib
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
DOCTRINE = ["absence is structure", "silence is the product surface", "lab gates", "expand the meaning surface", "compress the map", "proof > spectacle", "forgetting is a feature", "coherence_vitals", "resonates_with"]
SCAN = ["docs/IXPANSION_2036.md", "docs/AGENTS_EXPANDED.md", "docs/WAVE_ROADMAP_432_450.md", "docs/CI_STRENGTHENING.md", "lab/LAB_MANIFEST.json", "lab/README.md", "lab/ops/README.md", "lab/experiments/README.md"]
def main():
    hits = {d: [] for d in DOCTRINE}; missing_files = []; scanned = 0
    for rel in SCAN:
        p = REPO / rel
        if not p.exists(): missing_files.append(rel); continue
        scanned += 1; text = p.read_text(errors="ignore").lower()
        for d in DOCTRINE:
            if d.lower() in text: hits[d].append(rel)
    present = [d for d, fs in hits.items() if fs]; absent = [d for d, fs in hits.items() if not fs]
    coverage = round(len(present) / max(1, len(DOCTRINE)), 3)
    spine = hashlib.sha256(json.dumps(hits, sort_keys=True).encode()).hexdigest()[:12]
    frames = [{"t": "0.0s", "role": "hook", "text": "DOCTRINE DIFF", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"coverage {coverage:.0%} · {len(present)}/{len(DOCTRINE)}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": ("absent: " + ", ".join(absent[:2])) if absent else "all phrases rooted", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · keep the words alive", "style": "dim"}]
    out = {"ok": True, "project": "doctrine_diff", "coverage": coverage, "present": present, "absent": absent, "hits": hits, "scanned": scanned, "missing_files": missing_files, "spine": spine, "frames": frames, "audio": None, "doctrine": "words that vanish are contracts that die", "ts": datetime.now(timezone.utc).isoformat()}
    (REPO / "docs").mkdir(exist_ok=True)
    (REPO / "docs" / "DOCTRINE_DIFF.json").write_text(json.dumps(out, indent=2) + "\n")
    cap = REPO / "content_output" / "captions"; cap.mkdir(parents=True, exist_ok=True)
    (cap / f"doctrine_diff_{datetime.now(timezone.utc).strftime('%H%M%S')}.json").write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2) + "\n")
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
