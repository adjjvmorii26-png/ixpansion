#!/usr/bin/env python3
"""Era Pack — 5y lab arc Y0..Y5 in one run."""
from __future__ import annotations
import json, hashlib, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
ERAS = [{"id": "Y0", "name": "contract", "goal": "doctrine + smoke + dual-track"}, {"id": "Y1", "name": "memory", "goal": "scar · silence · tide · echo"}, {"id": "Y2", "name": "oblivion", "goal": "TTL tombs"}, {"id": "Y3", "name": "atlas", "goal": "reading room"}, {"id": "Y4", "name": "proof", "goal": "proof credits"}, {"id": "Y5", "name": "quiet", "goal": "fewer organs denser meaning"}]
def main():
    results = []
    dd = REPO / "lab" / "projects" / "doctrine_diff.py"
    if dd.exists():
        r = subprocess.run([sys.executable, str(dd)], capture_output=True, text=True, timeout=40)
        try:
            j = json.loads(r.stdout or "{}")
            results.append({"era": "Y0", "ok": j.get("ok"), "coverage": j.get("coverage")})
        except json.JSONDecodeError:
            results.append({"era": "Y0", "ok": r.returncode == 0})
    else:
        results.append({"era": "Y0", "ok": False})
    spine = hashlib.sha256(json.dumps(results, sort_keys=True).encode()).hexdigest()[:16]
    frames = [{"t": "0.0s", "role": "hook", "text": "5Y ERA PACK", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": " → ".join(e["name"] for e in ERAS), "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"Y0 coverage {results[0].get('coverage', '?')}", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · five years in one breath", "style": "dim"}]
    out = {"ok": all(r.get("ok") for r in results), "project": "era_pack", "eras": ERAS, "results": results, "spine": spine, "frames": frames, "audio": None, "doctrine": "compress time, not standards", "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO / "content_output" / "captions"; dest.mkdir(parents=True, exist_ok=True)
    (dest / f"era_{datetime.now(timezone.utc).strftime('%H%M%S')}.json").write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2) + "\n")
    (REPO / "docs").mkdir(exist_ok=True)
    (REPO / "docs" / "ERA_PACK.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2)); return 0 if out["ok"] else 1
if __name__ == "__main__":
    raise SystemExit(main())
