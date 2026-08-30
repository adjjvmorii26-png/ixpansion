"""Conclave — the full agent ceremony.

Scout surveys. Overseer decides. Gardener plants (when the move
warrants). Archivist writes. Chronicler remembers. In dry mode the
conclave proposes but touches nothing.

    python -m harbinger.conclave --dry
    python -m harbinger.conclave --idea "build a fortune engine"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harbinger.agents import scout, overseer, archivist, chronicler, dreamer
from harbinger.agents import gardener as gardener_agent
from harbinger import memory as conclave_memory


def ceremony(dry: bool = False, ideas: List[str] = None, commit: bool = True) -> Dict[str, Any]:
    report: Dict[str, Any] = {"mode": "dry" if dry else "live", "agents": {}}

    # 1. scout
    pulse = scout.run()
    report["agents"]["scout"] = pulse

    # 2. overseer
    choice = overseer.run(pulse, ideas=ideas)
    report["agents"]["overseer"] = choice
    proposal = choice["proposal"]

    # 2.5 dreamer — imagine future modules the frontier has not yet grown
    dreamscape = dreamer.run(tense=0.6)
    report["agents"]["dreamer"] = dreamscape
    if dreamscape.get("dreams"):
        # surface the freshest dream to the overseer as an available move
        report["dreams"] = [d["name"] for d in dreamscape["dreams"][:3]]

    conceived: Dict[str, Any] = {"title": proposal["title"], "work": proposal["work"]}

    # 3. gardener — only plants if the move is garden-flavored AND live
    if not dry and gardener_agent.is_garden_idea(proposal["title"]):
        words = proposal["work"][0] if proposal["work"] else "the frontier dreams onward"
        planted = gardener_agent.run(words, commit=commit)
        report["agents"]["gardener"] = planted
        conceived["planted"] = planted.get("name")

    # 4. archivist — live only
    if dry:
        report["agents"]["archivist"] = {
            "agent": "archivist", "version": archivist.mint(archivist._latest_version()),
            "would_write": f"## [{archivist.mint(archivist._latest_version())}] — {proposal['title']}"}
    else:
        saved = archivist.append(proposal["title"], body="\n".join(f"- {w}" for w in proposal["work"]))
        report["agents"]["archivist"] = saved
        conceived["version"] = saved.get("version")

    # 5. chronicler
    memory = chronicler.run() if not dry else {"agent": "chronicler", "written": False, "mode": "dry"}
    report["agents"]["chronicler"] = memory

    report["conceived"] = conceived

    # remember (live only)
    if not dry:
        try:
            conclave_memory.append({
                "mode": "live", "title": conceived["title"],
                "reason": choice.get("proposal", {}).get("reason"),
                "version": conceived.get("version"),
                "planted": conceived.get("planted"),
            })
            report["remembered"] = True
        except Exception:
            report["remembered"] = False

    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description="Harbinger — the self-watching conclave")
    ap.add_argument("--dry", action="store_true", help="propose without touching anything")
    ap.add_argument("--idea", action="append", default=[], help="an evolution idea for the overseer")
    ap.add_argument("--no-commit", action="store_true", help="garden without committing")
    args = ap.parse_args(argv)

    report = ceremony(dry=args.dry, ideas=args.idea, commit=not args.no_commit)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
