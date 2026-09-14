#!/usr/bin/env python3
"""Consent Lattice — allow/deny scopes for agent actions."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
REG = REPO / "lab" / "experiments" / "consent_registry.json"
DEFAULT = {"scopes": {"read_lab": True, "write_lab_experiments": True, "push_main": False, "delete_ci": False, "publish_youtube_meta": True, "external_network": False}}
def main():
    if REG.exists():
        try: reg = json.loads(REG.read_text())
        except json.JSONDecodeError: reg = DEFAULT
    else:
        reg = DEFAULT
        REG.write_text(json.dumps(reg, indent=2) + "\n")
    allowed = [k for k, v in reg.get("scopes", {}).items() if v]
    denied = [k for k, v in reg.get("scopes", {}).items() if not v]
    frames = [{"t": "0.0s", "role": "hook", "text": "CONSENT LATTICE", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"allow {len(allowed)} · deny {len(denied)}", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": ",".join(denied[:3]) or "none denied", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · consent before power", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "consent_lattice", "allowed": allowed, "denied": denied, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
