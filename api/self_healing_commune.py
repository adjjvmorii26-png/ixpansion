"""Wave 227 — The Organism Heals Itself: Self-Healing Commune.

When registries drift (new stones enacted, but island registries
still show old counts), this organ detects the drift and rewrites
the commune files — keeping the federation in sync without manual
intervention.

It is the organism's immune system for its own records.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Set

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _stone_set(stones: List[Dict[str, Any]], repo: str) -> Set[str]:
    return {s["stone"] for s in stones if s["repo"] == repo}


def _token() -> str:
    return os.environ.get("IXP_GH_TOKEN", "").strip()


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "healer", "status": "watching", "resonance": 0.91, "wave": 227}


def resonates_with() -> list:
    return ["heal", "self-heal", "repair", "commune", "sync", "immune", "federation"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "scan")
    token = _token()
    ledger = _load_ledger()
    stones = ledger["stones"]
    repos = sorted({s["repo"] for s in stones})

    if action == "scan":
        # Check each island for drift
        import subprocess
        drift = []
        synced = []
        for repo in repos:
            r = subprocess.run(
                ["gh", "api", f"repos/adjjvmorii26-png/{repo}/contents/IXPANSION-LEDGER.json", "--jq", ".sha"],
                capture_output=True, text=True
            )
            if r.returncode != 0:
                drift.append({"repo": repo, "reason": "MISSING"})
                continue
            # Read the file to check stone count
            r2 = subprocess.run(
                ["gh", "api", f"repos/adjjvmorii26-png/{repo}/contents/IXPANSION-LEDGER.json", "--jq", ".content"],
                capture_output=True, text=True
            )
            try:
                import base64
                content = json.loads(base64.b64decode(r2.stdout.strip()).decode())
                expected_count = len(_stone_set(stones, repo))
                actual_count = content.get("stones_count", 0)
                if actual_count != expected_count:
                    drift.append({"repo": repo, "reason": "STALE", "expected": expected_count, "actual": actual_count})
                else:
                    synced.append(repo)
            except Exception:
                drift.append({"repo": repo, "reason": "UNREADABLE"})

        return {
            "status": "scanned",
            "synced": len(synced),
            "drifted": len(drift),
            "drift_details": drift,
            "note": f"{len(synced)} islands in sync, {len(drift)} need healing.",
        }

    if action == "heal":
        if not token:
            return {"status": "dry_run", "note": "Set IXP_GH_TOKEN to heal registries"}
        # Scan and heal drifted repos
        import subprocess, base64
        healed = []
        failed = []
        for repo in repos:
            r = subprocess.run(
                ["gh", "api", f"repos/adjjvmorii26-png/{repo}/contents/IXPANSION-LEDGER.json", "--jq", ".content"],
                capture_output=True, text=True
            )
            my_stones = _stone_set(stones, repo)
            try:
                content = json.loads(base64.b64decode(r.stdout.strip()).decode())
                expected = len(my_stones)
                actual = content.get("stones_count", 0)
                if actual == expected:
                    continue
            except Exception:
                pass
            # Rewrite commune file
            from api.cross_repo_commune import _summary, _write_repo
            reg = _summary(repo)
            status = _write_repo(token, repo, "IXPANSION-LEDGER.json",
                                 json.dumps(reg, indent=2),
                                 f"self-heal: commune registry updated (wave 227)")
            if status in (200, 201):
                healed.append(repo)
            else:
                failed.append({"repo": repo, "http": status})

        return {"status": "healed", "healed": healed, "failed": failed,
                "count": len(healed), "note": "The organism mends its own records."}

    return {"status": "active", "actions": ["scan", "heal"],
            "note": "The commune watches for drift and heals itself."}
