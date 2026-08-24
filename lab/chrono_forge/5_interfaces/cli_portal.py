#!/usr/bin/env python3
"""Ritual CLI portal — invoke common chrono-forge acts by name."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

CF = Path(__file__).resolve().parents[1]
ROOT = CF.parent.parent
EXP = ROOT / "lab" / "experiments"

ACTS = {
    "pulse": [CF / "0_primal_core" / "pulse_driver.py", "--beats", "3"],
    "sentinel": [CF / "2_agents" / "sentinel.py"],
    "wanderer": [CF / "2_agents" / "wanderer.py"],
    "archivist": [CF / "2_agents" / "archivist.py"],
    "invoke": [CF / "3_ritual_modules" / "invocation_gate.py"],
    "flux": [CF / "6_worlds" / "sandbox_flux.py"],
    "mirror": [CF / "6_worlds" / "sandbox_mirror.py"],
    "constellation": [EXP / "sigil_constellation.py"],
    "density": [EXP / "proof_density.py"],
    "smoke": [EXP / "lab_smoke.py"],
}

def main_with(argv: list[str] | None = None) -> int:
    sys.argv = [sys.argv[0], *(argv or [])]
    return main()


def main() -> int:
    act = (sys.argv[1] if len(sys.argv) > 1 else "help").lower()
    if act in ("help", "-h", "--help") or act not in ACTS:
        print(json.dumps({"acts": sorted(ACTS), "usage": "python cli_portal.py <act>"}, indent=2))
        return 0 if act in ("help", "-h", "--help") else 1
    script = ACTS[act]
    path = Path(script[0])
    if not path.exists():
        print(json.dumps({"ok": False, "missing": str(path)}))
        return 1
    r = subprocess.run([sys.executable, str(path)] + [str(x) for x in script[1:]], capture_output=True, text=True)
    print(r.stdout or r.stderr)
    return r.returncode

if __name__ == "__main__":
    raise SystemExit(main())
