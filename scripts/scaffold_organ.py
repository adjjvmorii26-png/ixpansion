#!/usr/bin/env python3
"""Scaffold a new IXPANSION wave organ (api/waveNNN_name.py) from the canonical template.

Usage:
    python3 scripts/scaffold_organ.py --wave 752 --name gene_splicer
    python3 scripts/scaffold_organ.py -w 752 -n gene_splicer --actions status merge split
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = '''"""Wave {wave} — {name}.

{doc}
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave{wave}_{name}.json"
WAVE = {wave}
NAME = "{name}"

def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {{"wave": WAVE, "name": NAME, "events": [], "status": "seed"}}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {{"wave": WAVE, "name": NAME, "action": "status", "events": len(state.get("events", [])), "ok": True}}

    elif action == "ping":
        return {{"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}}

{actions_block}
    return {{"wave": WAVE, "name": NAME, "action": action, "ok": False, "error": "unknown_action"}}

def coherence_vitals() -> dict:
    state = _load()
    return {{"wave": WAVE, "name": NAME, "layer": "organ", "status": "active", "resonance": 0.5, "events": len(state.get("events", []))}}

def resonates_with() -> list:
    return [{resonates}]
'''

def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold an IXPANSION wave organ")
    parser.add_argument("--wave", "-w", type=int, required=True, help="wave number (e.g. 752)")
    parser.add_argument("--name", "-n", required=True, help="organ name in snake_case (e.g. gene_splicer)")
    parser.add_argument("--actions", required=False, help="comma-separated extra actions to stub")
    parser.add_argument("--resonates", required=False, default="720, 730, 751", help="comma-separated resonance list")
    args = parser.parse_args()

    api_file = ROOT / "api" / f"wave{args.wave}_{args.name}.py"
    if api_file.exists():
        print(f"ABORT: {api_file} already exists")
        return 1

    doc = (args.actions.replace("_", " ").title() if args.actions else
           f"A new organ for Wave {args.wave}.")

    actions_block = ""
    if args.actions:
        actions = [a.strip() for a in args.actions.split(",") if a.strip()]
        for a in actions:
            actions_block += f'''    elif action == "{a}":
        state.setdefault("events", []).append({{"action": "{a}", "at": datetime.datetime.now(datetime.UTC).isoformat()}})
        _save(state)
        return {{"wave": WAVE, "name": NAME, "action": "{a}", "ok": True, "count": len(state.get("events", []))}}

'''
    resonates = ", ".join(r.strip() for r in args.resonates.split(",") if r.strip())

    api_file.write_text(TEMPLATE.format(wave=args.wave, name=args.name, doc=doc,
                                         actions_block=actions_block, resonates=resonates))
    print(f"Created {api_file}")
    print(f"Next: wire into api/index.py, add tests/test_wave{args.wave}_{args.name}.py, bump versions.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
