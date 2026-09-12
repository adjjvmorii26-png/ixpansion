#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
EXPECTED = [
    ("chronoforge", "lab/CHRONOFORGE/runtime/cf_portal.py"),
    ("stratum", "lab/STRATUM_ENGINE/runtime/se_portal.py"),
    ("monolith", "lab/MONOLITH_STACK/runtime/ms_portal.py"),
    ("helix", "lab/helix_bridge/probe.py"),
    ("polygenesis", "lab/polygenesis/pg_portal.py"),
    ("chronoweave", "lab/chronoweave/cw_portal.py"),
    ("paradox", "lab/paradox_forge/pf_portal.py"),
    ("comet", "lab/proof_comet/build_data.py"),
    ("openclaw", "lab/openclaw/portal.py"),
    ("wasm_lattice", "lab/wasm/lattice_core.wasm"),
]
def main():
    present, absent = [], []
    for name, rel in EXPECTED:
        (present if (REPO / rel).exists() else absent).append({"name": name, "path": rel})
    print(json.dumps({"ok": True, "project": "null_orchard", "present": len(present), "absent": len(absent), "voids": absent, "note": "absence is a first-class signal", "ts": datetime.now(timezone.utc).isoformat()}, indent=2))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
