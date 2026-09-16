#!/usr/bin/env python3
"""Subprocess vitals — true isolation for dirty in-memory organs.

Runs coherence_vitals() in a fresh Python process so modules like
coherence_regulator / waves 190–197 cannot leak state into the parent.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]

_WORKER = r'''
import json, sys
from pathlib import Path
import importlib.util
path = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("iso_" + path.stem, path)
if not spec or not spec.loader:
    print(json.dumps({"ok": False, "error": "no_spec", "module": path.stem}))
    sys.exit(0)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except Exception as e:
    print(json.dumps({"ok": False, "error": type(e).__name__, "module": path.stem}))
    sys.exit(0)
fn = getattr(mod, "coherence_vitals", None)
if not callable(fn):
    print(json.dumps({"ok": False, "error": "no_vitals", "module": path.stem}))
    sys.exit(0)
try:
    v = fn()
    if not isinstance(v, dict):
        v = {"ok": False, "error": "bad_vitals", "module": path.stem}
    else:
        v.setdefault("module", path.stem)
        v.setdefault("ok", True)
    print(json.dumps(v, default=str))
except Exception as e:
    print(json.dumps({"ok": False, "error": type(e).__name__, "module": path.stem}))
'''


def vitals_isolated(path: Path, timeout: float = 15.0) -> Dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        return {"ok": False, "error": "missing", "module": path.stem}
    try:
        proc = subprocess.run(
            [sys.executable, "-c", _WORKER, str(path.resolve())],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(ROOT),
        )
        out = (proc.stdout or "").strip().splitlines()
        if not out:
            return {
                "ok": False,
                "error": "empty_stdout",
                "module": path.stem,
                "stderr": (proc.stderr or "")[:200],
            }
        return json.loads(out[-1])
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout", "module": path.stem}
    except Exception as e:
        return {"ok": False, "error": type(e).__name__, "module": path.stem}


def main(argv=None) -> int:
    argv = list(argv or sys.argv[1:])
    if not argv:
        print(json.dumps({"error": "usage: subprocess_vitals.py <module.py>"}))
        return 2
    print(json.dumps(vitals_isolated(Path(argv[0])), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
