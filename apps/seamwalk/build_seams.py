#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, hashlib, math
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "seams.json"
def jrun(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return json.loads(r.stdout or "{}")
    except Exception:
        return {}
def main():
    null = jrun([sys.executable, str(REPO / "lab" / "null_orchard" / "map_absence.py")])
    mood = jrun([sys.executable, str(REPO / "lab" / "merkle_mood" / "mood.py")])
    helix = {}
    hp = REPO / "lab" / "helix_bridge" / "constellation.json"
    if hp.exists():
        try: helix = json.loads(hp.read_text())
        except json.JSONDecodeError: pass
    seams = []
    for name in ["chronoforge", "stratum", "monolith", "helix", "polygenesis", "chronoweave", "paradox"]:
        seams.append({"id": name, "kind": "plate", "tension": 0.15, "label": name})
    for v in null.get("voids") or []:
        seams.append({"id": v.get("name", "void"), "kind": "rift", "tension": 0.85, "label": f"∅ {v.get('name')}", "path": v.get("path")})
    for n in helix.get("nodes") or []:
        seams.append({"id": f"hx_{n.get('name')}", "kind": "pulse" if n.get("ok") else "fault", "tension": 0.2 if n.get("ok") else 0.9, "label": n.get("name")})
    field = []
    for i, s in enumerate(seams):
        ang = (i / max(len(seams), 1)) * 2 * math.pi
        r = 0.35 + 0.4 * s["tension"]
        h = hashlib.sha256(s["id"].encode()).hexdigest()
        field.append({**s, "x": round(math.cos(ang) * r, 4), "y": round(math.sin(ang) * r, 4), "hue": int(h[:2], 16) % 360})
    data = {"title": "SEAMWALK", "channel": "@CoodingLooop", "mood": mood.get("mood", "void"), "primary": mood.get("primary", "#00e5ff"), "secondary": mood.get("secondary", "#ff2bd6"), "n_seams": len(field), "field": field, "doctrine": "absence is structure", "ts": datetime.now(timezone.utc).isoformat()}
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({"ok": True, "wrote": str(OUT), "n": len(field)}, indent=2))
if __name__ == "__main__":
    main()
