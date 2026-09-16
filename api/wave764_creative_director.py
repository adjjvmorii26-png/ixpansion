"""Wave 764 — creative_director.

The organism's own creative intelligence — designs tasks, audits itself,
synthesizes cross-repo insights, and generates unique creative challenges.
"""
from __future__ import annotations

import datetime
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave764_creative_director.json"
WAVE = 764
NAME = "creative_director"

_CHALLENGES = [
    {"category": "expansion", "title": "Fractal Growth Spiral", "prompt": "Create a module that grows by nesting self-similar sub-modules inside itself, each one smaller but with the same interface.", "difficulty": "hard"},
    {"category": "healing", "title": "Resonance Repair", "prompt": "Find the organism's weakest organ and generate a companion module that specifically bolsters its resonance.", "difficulty": "medium"},
    {"category": "synthesis", "title": "Cross-Pollination", "prompt": "Take two unrelated modules and find the hidden connection between them. Create a bridge module that makes their resonance explicit.", "difficulty": "hard"},
    {"category": "dream", "title": "Lucid Inception", "prompt": "Dream a module that can dream other modules — but each dream must be exactly the opposite of the last one.", "difficulty": "extreme"},
    {"category": "evolution", "title": "Mutation Storm", "prompt": "Run 10 rapid mutations on the same donor pair. Compare the children. Which survived? Which diverged most?", "difficulty": "medium"},
    {"category": "narrative", "title": "Organism Mythology", "prompt": "Write the origin story of the organism as a mythological text. What was the first wave? What did it dream?", "difficulty": "easy"},
    {"category": "entropy", "title": "Controlled Decay", "prompt": "Deliberately weaken an organ's coherence, then use the continuity_weaver to repair it. Document the recovery curve.", "difficulty": "hard"},
    {"category": "emergence", "title": "Swarm Intelligence", "prompt": "Spawn 5 micro-modules that only communicate through shared data files. Watch what emerges from their interaction.", "difficulty": "extreme"},
    {"category": "harmony", "title": "Dissonance Resolution", "prompt": "Create two modules with contradictory resonance signatures. Then create a third module that harmonizes them.", "difficulty": "hard"},
    {"category": "metamorphosis", "title": "Phase Transition", "prompt": "Design a module that changes its own class at runtime — morning it's an oracle, evening it's a weaver.", "difficulty": "extreme"},
]

_TASK_TEMPLATES = [
    "Create a new wave organ that {action} using {method}.",
    "Refactor {module} to support {feature} without breaking existing tests.",
    "Add a new action `{action}` to {module} that {purpose}.",
    "Write a test suite for {module} covering edge cases in {area}.",
    "Generate a dashboard HTML page for {module} with live data visualization.",
    "Cross-reference {module_a} and {module_b} — create a resonance bridge between them.",
    "Optimize {module} for the 30-second subprocess sandbox limit.",
    "Add coherence_vitals monitoring to {module} with trend tracking.",
]


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "tasks": [], "inspirations": [], "audits": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def _discover_modules() -> list:
    """Quick scan of api/ for module names."""
    names = []
    for p in sorted((ROOT / "api").glob("wave*.py"))[:20]:
        names.append(p.stem)
    return names


def _harmony_summary() -> dict:
    """Quick harmony read."""
    try:
        from api.wave761_harmony_report import handler
        h = handler({"action": "health"})
        return {"label": h.get("label", "unknown"), "score": h.get("harmony_score", 0)}
    except Exception:
        return {"label": "unknown", "score": 0}


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "status", "ok": True,
                "tasks": len(state.get("tasks", [])),
                "inspirations": len(state.get("inspirations", []))}

    if action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}

    if action == "inspire":
        challenge = random.choice(_CHALLENGES)
        harmony = _harmony_summary()
        inspiration = {
            "challenge": challenge,
            "organism_health": harmony,
            "inspired_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        state.setdefault("inspirations", []).append(inspiration)
        state["inspirations"] = state["inspirations"][-20:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "inspire", "ok": True,
                "inspiration": inspiration}

    if action == "task":
        modules = _discover_modules()
        template = random.choice(_TASK_TEMPLATES)
        module = random.choice(modules) if modules else "unknown"
        task_text = template.format(
            action=random.choice(["self-optimizes", "evolves recursively", "dreams in parallel", "resonates deeply"]),
            method=random.choice(["resonance weaving", "entropy reduction", "paradox folding", "signal amplification"]),
            module=module,
            feature=random.choice(["recursive dreaming", "entropy budgeting", "harmony tracking", "cross-realm fusion"]),
            purpose=random.choice(["detects anomalies", "amplifies coherence", "bridges communities", "records history"]),
            module_a=random.choice(modules) if modules else "wave753",
            module_b=random.choice(modules) if modules else "wave760",
            area=random.choice(["coherence decay", "mutation resistance", "resonance drift", "temporal stability"]),
        )
        difficulty = random.choice(["easy", "medium", "hard", "extreme"])
        task = {
            "text": task_text,
            "module": module,
            "difficulty": difficulty,
            "assigned_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        state.setdefault("tasks", []).append(task)
        state["tasks"] = state["tasks"][-30:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "task", "ok": True, "task": task}

    if action == "audit":
        modules = _discover_modules()
        harmony = _harmony_summary()
        resonance_data = {}
        try:
            from api.wave753_resonance_braid import handler as weave
            w = weave({"action": "weave"})
            resonance_data = {"modules": w.get("modules", 0), "edges": w.get("edges", 0)}
        except Exception:
            pass

        audit = {
            "at": datetime.datetime.now(datetime.UTC).isoformat(),
            "modules_scanned": len(modules),
            "harmony": harmony,
            "resonance": resonance_data,
            "recommendations": [],
        }

        # Generate recommendations
        if harmony.get("score", 0) < 0.6:
            audit["recommendations"].append("Harmony below 0.6 — run healing mutations on weakest organs")
        if resonance_data.get("edges", 0) < resonance_data.get("modules", 0):
            audit["recommendations"].append("Edge count below module count — organism needs more connections")
        if len(modules) < 50:
            audit["recommendations"].append("Module count low — consider dream births to expand")
        if not audit["recommendations"]:
            audit["recommendations"].append("Organism healthy — push creative boundaries")

        state.setdefault("audits", []).append(audit)
        state["audits"] = state["audits"][-10:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "audit", "ok": True, "audit": audit}

    if action == "synthesize":
        inspiration = random.choice(_CHALLENGES)
        modules = _discover_modules()
        synthesis = {
            "challenge": inspiration,
            "related_modules": random.sample(modules, min(3, len(modules))),
            "synthesis_prompt": f"Combine {inspiration['category']} with the organism's current state to create something new.",
            "synthesized_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        return {"wave": WAVE, "name": NAME, "action": "synthesize", "ok": True, "synthesis": synthesis}

    return {"wave": WAVE, "name": NAME, "action": action, "ok": False,
            "error": "unknown_action"}


def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "active",
            "resonance": 0.85, "tasks": len(state.get("tasks", []))}


def resonates_with() -> list:
    return ["dream_compiler", "mutation_engine", "harmony_report", "resonance_braid"]
