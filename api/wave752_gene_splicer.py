"""Wave 752 — gene_splicer.

Status,Merge,Split
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave752_gene_splicer.json"
WAVE = 752
NAME = "gene_splicer"

def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "events": [], "status": "seed"}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "status", "events": len(state.get("events", [])), "ok": True}

    elif action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}

    elif action == "splice":
        donor_a = req.get("donor_a") or "wave734_repo_dna"
        donor_b = req.get("donor_b") or "wave751_evolution_kernel"
        try:
            from api.wave734_repo_dna import _load_repo_profiles
            profiles = _load_repo_profiles()
        except Exception:
            profiles = {}
        pa = profiles.get(donor_a, {})
        pb = profiles.get(donor_b, {})
        if not pa or not pb:
            return {"wave": WAVE, "name": NAME, "action": "splice", "ok": False,
                    "error": "one donor DNA not found", "found": list(profiles.keys())[:5]}
        # Splice: paradigm from lower complexity donor, patterns mixed, skills union
        complexity_a = pa.get("complexity", 5)
        complexity_b = pb.get("complexity", 5)
        dominant = pa if complexity_a >= complexity_b else pb
        recessive = pb if complexity_a >= complexity_b else pa
        child = {
            "donor_a": donor_a,
            "donor_b": donor_b,
            "paradigm": f"{recessive.get('paradigm', 'organ')}->{dominant.get('paradigm', 'organ')}",
            "patterns": sorted(set(pa.get("patterns", []) + pb.get("patterns", []))),
            "complexity": round((complexity_a + complexity_b) / 2, 1),
            "test_success": round((pa.get("test_success", 0.9) + pb.get("test_success", 0.9)) / 2, 3),
            "skills": sorted(set(
                [f"{t}_{dominant.get('paradigm','organ')}" for t in ("splice", "hybrid", "express")]
                + [f"echo_{t}" for t in recessive.get("patterns", [])[:2]]
            )),
            "spliced_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        state.setdefault("events", []).append(child)
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "splice", "ok": True, "child_dna": child}

    elif action == "merge":
        donor_a = req.get("donor_a") or "wave734_repo_dna"
        donor_b = req.get("donor_b") or "wave751_evolution_kernel"
        try:
            from api.wave734_repo_dna import _load_repo_profiles
            profiles = _load_repo_profiles()
        except Exception:
            profiles = {}
        merged = {k: v for k, v in {**profiles.get(donor_a, {}), **profiles.get(donor_b, {})}.items()}
        merged["parentage"] = [donor_a, donor_b]
        state.setdefault("events", []).append({"action": "merge", "parents": merged["parentage"]})
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "merge", "ok": True, "merged": merged}

    elif action == "split":
        donor = req.get("donor") or "wave734_repo_dna"
        try:
            from api.wave734_repo_dna import _load_repo_profiles
            profiles = _load_repo_profiles()
        except Exception:
            profiles = {}
        prof = profiles.get(donor, {})
        patterns = prof.get("patterns", [])
        halves = [{"parent": donor, "trait": p} for p in patterns[:2]] or [{"parent": donor, "trait": "identity"}]
        state.setdefault("events", []).append({"action": "split", "halves": halves})
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "split", "ok": True, "halves": halves}

    return {"wave": WAVE, "name": NAME, "action": action, "ok": False, "error": "unknown_action"}


def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "active", "resonance": 0.5, "events": len(state.get("events", []))}

def resonates_with() -> list:
    return [734, 751]
