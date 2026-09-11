#!/usr/bin/env python3
"""Fast lab smoke — compile key modules + helix ethics probes."""
from __future__ import annotations
import compileall, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "lab" / "helix_bridge",
    ROOT / "lab" / "STRATUM_ENGINE",
    ROOT / "lab" / "proof_comet",
    ROOT / "lab" / "unique_projects",
]
ok = True
results = []
for t in TARGETS:
    if not t.exists():
        results.append({"path": str(t), "ok": False, "err": "missing"})
        ok = False
        continue
    c = compileall.compile_dir(str(t), quiet=1)
    results.append({"path": t.name, "compile": bool(c)})
    ok &= bool(c)
probe = ROOT / "lab" / "helix_bridge" / "probe.py"
if probe.exists():
    r = subprocess.run([sys.executable, str(probe)], capture_output=True, text=True, timeout=90)
    results.append({"helix": r.returncode == 0})
    ok &= r.returncode == 0
print(json.dumps({"ok": ok, "smoke": "lab", "results": results}, indent=2))
raise SystemExit(0 if ok else 1)
