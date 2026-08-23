#!/usr/bin/env python3
"""Boot ritual: sigils → pulse → sentinel → wanderer → forge_mind → chronicle → observer."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

CF = Path(__file__).resolve().parents[1]

def _run(script: str, args: list | None = None) -> dict:
    cmd = [sys.executable, str(CF / script)] + (args or [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    return {"ok": r.returncode == 0, "out": (r.stdout or "")[-400:], "err": (r.stderr or "")[-200:]}

def run() -> dict:
    steps = []
    steps.append({"step": "sigil_registry", **_run("0_primal_core/sigil_registry.py")})
    steps.append({"step": "pulse", **_run("0_primal_core/pulse_driver.py", ["--beats", "3"])})
    steps.append({"step": "sentinel", **_run("2_agents/sentinel.py")})
    steps.append({"step": "wanderer", **_run("2_agents/wanderer.py")})
    steps.append({"step": "forge_mind", **_run("2_agents/forge_mind.py", ["NODE status"])})
    steps.append({"step": "mirror", **_run("6_worlds/sandbox_mirror.py")})
    chron = CF / "7_lore" / "chronicles" / "chronicle.jsonl"
    chron.parent.mkdir(parents=True, exist_ok=True)
    line = {"ts": datetime.now(timezone.utc).isoformat(), "event": "invocation_v2", "steps": [s["step"] for s in steps], "ok": all(s.get("ok") for s in steps)}
    with chron.open("a") as f:
        f.write(json.dumps(line) + "\n")
    steps.append({"step": "chronicle", "ok": True})
    steps.append({"step": "observer", **_run("8_meta/observer_log.py", ["invocation_gate"])})
    return {"ritual": "invocation_gate_v2", "steps": steps, "ok": all(s.get("ok") for s in steps)}

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
