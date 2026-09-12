#!/usr/bin/env python3
"""Fast lab smoke — compile present modules; soft-skip missing; helix if present."""
from __future__ import annotations
import compileall, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
# required: must exist and compile
REQUIRED = [
    ROOT / "lab" / "helix_bridge",
    ROOT / "lab" / "ops",
]
# optional: skip if absent
OPTIONAL = [
    ROOT / "lab" / "STRATUM_ENGINE",
    ROOT / "lab" / "proof_comet",
    ROOT / "lab" / "unique_projects",
    ROOT / "lab" / "pulse_echo",
    ROOT / "lab" / "null_orchard",
    ROOT / "lab" / "merkle_mood",
]
ok = True
results = []
for t in REQUIRED:
    if not t.exists():
        results.append({"path": t.name, "ok": False, "err": "missing_required"})
        ok = False
        continue
    c = compileall.compile_dir(str(t), quiet=1)
    results.append({"path": t.name, "compile": bool(c), "required": True})
    ok &= bool(c)
for t in OPTIONAL:
    if not t.exists():
        results.append({"path": t.name, "status": "skip"})
        continue
    c = compileall.compile_dir(str(t), quiet=1)
    results.append({"path": t.name, "compile": bool(c), "required": False})
    ok &= bool(c)
probe = ROOT / "lab" / "helix_bridge" / "probe.py"
if probe.exists():
    r = subprocess.run([sys.executable, str(probe)], capture_output=True, text=True, timeout=90)
    results.append({"helix": r.returncode == 0})
    ok &= r.returncode == 0
print(json.dumps({"ok": ok, "smoke": "lab", "results": results}, indent=2))
raise SystemExit(0 if ok else 1)
