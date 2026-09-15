#!/usr/bin/env python3
"""Promote Manifest — additive-only paths safe to PR into main."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
SAFE_GLOBS = ["lab/experiments/*.py", "lab/evolve/*.py", "tests/test_*.py", "docs/SAFE_ROUTES.md", "docs/LAB_SYNC.md", "docs/EXPANSION_IDEAS.md"]
DENY = ["ci.yml", "ci-v2.yml", ".github/workflows", "api/wave", "DELETE"]
PRIORITY = [
    "lab/experiments/citizen_opcode.py",
    "lab/experiments/proof_bloom_gate.py",
    "lab/experiments/proof_bloom.py",
    "lab/experiments/hex_from_consent.py",
    "lab/experiments/hex_from_mercy.py",
    "lab/experiments/hex_bundle.py",
    "lab/experiments/consent_lattice.py",
    "lab/experiments/fast_board.py",
    "docs/SAFE_ROUTES.md",
]
def main():
    present = [rel for rel in PRIORITY if (REPO / rel).exists()]
    frames = [{"t": "0.0s", "role": "hook", "text": "PROMOTE MANIFEST", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{len(present)} safe paths", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": present[0].split("/")[-1] if present else "none", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · promote by file", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "promote_manifest", "safe_globs": SAFE_GLOBS, "deny_substrings": DENY, "priority_present": present, "policy": "additive only · no CI deletes · no wave test removal", "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
