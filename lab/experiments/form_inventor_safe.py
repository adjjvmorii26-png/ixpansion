#!/usr/bin/env python3
"""Propose a new form id, gated by recursion_anchor."""
from __future__ import annotations
import hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent

def invent() -> dict:
    r = subprocess.run([sys.executable, str(HERE / "recursion_anchor.py"), "form_inventor"], capture_output=True, text=True)
    gate = json.loads(r.stdout)
    if not gate.get("ok"):
        return {"invented": False, **gate}
    h = hashlib.sha256(datetime.now(timezone.utc).isoformat().encode()).hexdigest()[:8]
    form_id = f"form_{h}"
    reg_path = HERE / "form_registry.json"
    reg = json.loads(reg_path.read_text()) if reg_path.exists() else {"forms": []}
    reg.setdefault("forms", []).append({"id": form_id, "status": "proposed"})
    reg_path.write_text(json.dumps(reg, indent=2) + "\n")
    subprocess.run([sys.executable, str(HERE / "recursion_anchor.py"), "reset"], capture_output=True)
    return {"invented": True, "form_id": form_id, "gate": gate}

if __name__ == "__main__":
    print(json.dumps(invent(), indent=2))
