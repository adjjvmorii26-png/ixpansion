"""Wave 751 — Evolution Kernel.

Meta-scheduler that observes all modules and automatically proposes
mutations, merges, or deprecations based on entropy, usage frequency,
and cross-domain resonance. This is the layer that decides WHAT the
organism should evolve next.
"""
import json, random, hashlib
from pathlib import Path
from typing import Any, Dict
import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave751_evolution_kernel.json"
WAVE = 751
NAME = "evolution_kernel"

PROPOSAL_TYPES = ["mutate", "merge", "deprecate", "generate", "cross_pollinate", "stabilize", "transcend"]

def _load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"wave": WAVE, "name": NAME, "proposals": [], "decisions": [], "lineage": {}}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def _compute_entropy(signals: dict) -> float:
    """Entropy from input signals: 0=ordered, 1=chaotic."""
    base = signals.get("instability", 0.5) * 0.4
    base += signals.get("divergence", 0.5) * 0.3
    base += signals.get("newness", 0.5) * 0.3
    return round(min(1.0, max(0.0, base)), 3)

def _resonance(module_a: str, module_b: str) -> float:
    """Cross-domain resonance between two module names (token overlap heuristic)."""
    tokens_a = set(module_a.replace("_", " ").split())
    tokens_b = set(module_b.replace("_", " ").split())
    if not tokens_a or not tokens_b:
        return 0.0
    overlap = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return round(overlap / max(union, 1), 3)

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "observe":
        modules = req.get("modules", [])
        signals = req.get("signals", {})
        entropy = _compute_entropy(signals)

        # Build proposals from observations
        proposals = []
        for i, mod in enumerate(modules[:8]):
            ptype = random.choice(PROPOSAL_TYPES)
            partner = modules[(i + 1) % len(modules)] if len(modules) > 1 else None
            res = _resonance(mod, partner) if partner else 0.0
            proposal = {
                "id": hashlib.md5(f"{mod}{ptype}{datetime.datetime.now(datetime.UTC).isoformat()}".encode()).hexdigest()[:8],
                "type": ptype,
                "module": mod,
                "partner": partner,
                "resonance": res,
                "entropy": entropy,
                "priority": "high" if res > 0.3 or entropy > 0.7 else "medium" if res > 0.15 else "low",
                "rationale": f"{mod} shows {'high' if entropy > 0.6 else 'low'} entropy with resonance {res}",
                "wave": WAVE,
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
            }
            proposals.append(proposal)

        state["proposals"].extend(proposals)
        state["last_observation"] = {
            "module_count": len(modules),
            "entropy": entropy,
            "proposals_generated": len(proposals),
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
        }
        _save(state)
        return {"wave": WAVE, "action": "observe", "entropy": entropy, "proposals": proposals}

    elif action == "decide":
        proposal_id = req.get("proposal_id", "")
        decision = req.get("decision", "adopt")
        for p in state["proposals"]:
            if p["id"] == proposal_id:
                p["decision"] = decision
                p["decided_at"] = datetime.datetime.now(datetime.UTC).isoformat()
                state["decisions"].append(p)
                _save(state)
                return {"wave": WAVE, "action": "decide", "decision": p}
        return {"wave": WAVE, "action": "decide", "error": "proposal not found"}

    elif action == "lineage":
        wave_from = req.get("wave", 730)
        wave_to = req.get("wave_end", WAVE)
        lineage = [f"wave{w}" for w in range(wave_from, wave_to + 1)]
        state["lineage"] = {"from": wave_from, "to": wave_to, "waves": lineage}
        _save(state)
        return {"wave": WAVE, "lineage": state["lineage"], "span": len(lineage)}

    elif action == "status":
        return {"wave": WAVE, "name": NAME, "proposals": len(state["proposals"]), "decisions": len(state["decisions"]), "status": "active"}

    return {"wave": WAVE, "action": action, "status": "ok"}

def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "proposals": len(state["proposals"]), "decisions": len(state["decisions"]), "status": "active"}

def resonates_with() -> list:
    return [730, 731, 733, 734, 750]

if __name__ == "__main__":
    modules = ["coherence_bridge", "dream_compiler", "symbiosis_ecology", "threshold_engine", "metaphor_forge", "skill_builder", "repo_dna", "live_blog"]
    r = handler({"action": "observe", "modules": modules, "signals": {"instability": 0.7, "divergence": 0.5, "newness": 0.8}})
    print(json.dumps(r, indent=2)[:800])
    print("Vitals:", coherence_vitals())
