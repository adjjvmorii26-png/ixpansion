"""Wave 760 — mutation_engine.

Applies Gene Splicer mutation patterns across the 914+ module canvas.
- mutates repo DNA by cross-breeding paradigms
- expresses new skills from mutated DNA
- propagates mutations through resonance graph
- visualizes the organism's evolutionary canvas
"""
from __future__ import annotations

import datetime
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave760_mutation_engine.json"
WAVE = 760
NAME = "mutation_engine"

_PARADIGMS = [
    "asynchronous", "data_pipeline", "metaprogramming", "agent_based",
    "event_driven", "state_machine", "creative_synthesis", "introspection",
    "meta_programming", "registry_pattern", "actor_model", "concurrent",
    "full_stack", "code_generation", "symbolic", "quantum",
    "bio_mimetic", "temporal", "federated", "emergent"
]

_PATTERNS_BY_PARADIGM = {
    "asynchronous": ["import", "async", "context_manager", "await", "gather"],
    "data_pipeline": ["import", "json", "serialization", "transform", "stream"],
    "metaprogramming": ["import", "meta", "reflection", "exec", "compile"],
    "agent_based": ["import", "class", "agent", "message", "behavior"],
    "event_driven": ["import", "signal", "handler", "emit", "subscribe"],
    "state_machine": ["import", "state", "transition", "guard", "action"],
    "creative_synthesis": ["import", "transform", "generate", "compose", "remix"],
    "introspection": ["import", "reflect", "examine", "inspect", "query"],
    "meta_programming": ["import", "exec", "dynamic", "type", "proxy"],
    "registry_pattern": ["import", "register", "lookup", "discover", "resolve"],
    "actor_model": ["import", "concurrent", "message", "mailbox", "supervise"],
    "concurrent": ["import", "async", "queue", "lock", "semaphore"],
    "full_stack": ["import", "route", "render", "middleware", "auth"],
    "code_generation": ["import", "template", "scaffold", "ast", "emit"],
    "symbolic": ["import", "symbol", "reason", "infer", "prove"],
    "quantum": ["import", "qubit", "superposition", "entangle", "measure"],
    "bio_mimetic": ["import", "cell", "evolve", "mutate", "select"],
    "temporal": ["import", "time", "history", "replay", "branch"],
    "federated": ["import", "peer", "consensus", "sync", "replicate"],
    "emergent": ["import", "pattern", "self_organize", "feedback", "adapt"],
}


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "mutations": [], "expressed_skills": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def _all_wave_modules() -> List[str]:
    """Get all wave module names from api/"""
    names = []
    for p in (ROOT / "api").glob("wave*.py"):
        m = p.name.match(r"wave(\d+)_(.+)\.py") if hasattr(p.name, 'match') else None
        # Use regex
    import re
    for p in (ROOT / "api").glob("wave*.py"):
        m = re.match(r"wave\d+_(.+)\.py", p.name)
        if m:
            names.append(m.group(1))
    return sorted(names)


def _load_repo_profiles() -> Dict[str, dict]:
    """Load repo DNA profiles from wave734."""
    try:
        from api.wave734_repo_dna import _load_repo_profiles
        return _load_repo_profiles()
    except Exception:
        return {}


def _mutate_dna(donor_a: dict, donor_b: dict) -> dict:
    """Splice two DNA profiles into a child."""
    complexity_a = donor_a.get("complexity", 5)
    complexity_b = donor_b.get("complexity", 5)
    dominant = donor_a if complexity_a >= complexity_b else donor_b
    recessive = donor_b if complexity_a >= complexity_b else donor_a

    # Paradigm shift: dominant with recessive influence
    child_paradigm = f"{recessive.get('paradigm','organ')}->{dominant.get('paradigm','organ')}"
    
    # Mixed patterns
    patterns = sorted(set(donor_a.get("patterns", []) + donor_b.get("patterns", [])))
    
    # Complexity and success averaged with variance
    complexity = round((complexity_a + complexity_b) / 2 + random.uniform(-1, 1), 1)
    test_success = round((donor_a.get("test_success", 0.9) + donor_b.get("test_success", 0.9)) / 2 + random.uniform(-0.02, 0.02), 3)
    test_success = max(0.7, min(0.99, test_success))

    # New skills from paradigm fusion
    new_skills = []
    for p in patterns[:3]:
        new_skills.append(f"{p}_{dominant.get('paradigm', 'organ')}")
    for p in recessive.get("patterns", [])[:2]:
        new_skills.append(f"echo_{p}")

    return {
        "donor_a": donor_a.get("paradigm", "unknown"),
        "donor_b": donor_b.get("paradigm", "unknown"),
        "paradigm": child_paradigm,
        "patterns": patterns,
        "complexity": complexity,
        "test_success": test_success,
        "skills": new_skills,
        "mutated_at": datetime.datetime.now(datetime.UTC).isoformat(),
    }


def _express_skill_from_dna(dna: dict) -> dict:
    """Generate a Codex skill from mutated DNA."""
    paradigm = dna.get("paradigm", "emergent")
    patterns = dna.get("patterns", [])
    
    # Create skill name from paradigm
    skill_name = f"{paradigm.replace('->', '_')}_engine"
    
    commands = []
    for p in patterns[:3]:
        commands.append(f"{p}_action")
    commands.append("mutate")
    
    return {
        "name": skill_name,
        "paradigm": paradigm,
        "commands": commands,
        "roots": "r1",
        "category": "organism",
        "tags": ["mutation", "expressed", paradigm],
        "expressed_at": datetime.datetime.now(datetime.UTC).isoformat(),
    }

SKILLS_DIR = ROOT / "skills" / "r1"

def _write_skill_to_disk(skill: dict) -> str:
    """Write a SKILL.md file to skills/r1/<name>/."""
    name = skill.get("name", "unknown")
    safe_name = name.replace("->", "_").replace(" ", "_")
    skill_dir = SKILLS_DIR / safe_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    md_path = skill_dir / "SKILL.md"

    commands = skill.get("commands", [])
    tags = skill.get("tags", [])
    paradigm = skill.get("paradigm", "unknown")

    lines = [
        "---",
        f"name: {safe_name}",
        f"description: Organism-expressed skill from paradigm {paradigm}",
        f"tags: [{', '.join(tags)}]",
        "---",
        "",
        f"# {safe_name}",
        "",
        "## Origin",
        f"Expressed from mutated DNA — paradigm: {paradigm}",
        "",
        "## Commands",
    ]
    for cmd in commands:
        lines.append(f"- `{cmd}` — perform {cmd} action")
    lines += [
        "",
        "## Integration",
        f"- Category: {skill.get('category', 'organism')}",
        "- Roots: r1",
        f"- Expressed: {skill.get('expressed_at', 'unknown')}",
        "",
    ]

    md_path.write_text("\n".join(lines))
    return str(md_path)

def _propagate(mutations: List[dict], modules: List[str]) -> Dict[str, Any]:
    """Propagate mutations through the module canvas via resonance."""
    # Get resonance graph from wave753
    try:
        from api.wave753_resonance_braid import _graph as get_graph
        g = get_graph()
    except Exception:
        g = {}
    
    affected = {}
    for m in mutations:
        paradigm = m.get("paradigm", "")
        # Find modules that share paradigm tokens
        for mod in modules:
            mod_tokens = set(mod.split("_"))
            paradigm_tokens = set(paradigm.split("->"))
            if mod_tokens & paradigm_tokens:
                affected.setdefault(mod, []).append(paradigm)
    
    return {
        "total_modules": len(modules),
        "affected_modules": len(affected),
        "propagation_map": {k: list(set(v)) for k, v in affected.items()},
    }


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()
    profiles = _load_repo_profiles()
    modules = _all_wave_modules()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "status", "ok": True,
                "mutations": len(state.get("mutations", [])),
                "expressed_skills": len(state.get("expressed_skills", [])),
                "available_donors": len(profiles),
                "canvas_modules": len(modules)}

    if action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}

    if action == "mutate":
        donor_a = req.get("donor_a", random.choice(list(profiles.keys())) if profiles else "wave734_repo_dna")
        donor_b = req.get("donor_b", random.choice(list(profiles.keys())) if profiles else "wave751_evolution_kernel")
        
        pa = profiles.get(donor_a, {})
        pb = profiles.get(donor_b, {})
        if not pa or not pb:
            return {"wave": WAVE, "name": NAME, "action": "mutate", "ok": False,
                    "error": "donor_not_found", "available": list(profiles.keys())[:10]}
        
        child = _mutate_dna(pa, pb)
        state.setdefault("mutations", []).append(child)
        state["mutations"] = state["mutations"][-50:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "mutate", "ok": True, "child_dna": child}

    if action == "express":
        if not state.get("mutations"):
            return {"wave": WAVE, "name": NAME, "action": "express", "ok": False,
                    "error": "no_mutations_to_express"}
        dna = state["mutations"][-1]
        skill = _express_skill_from_dna(dna)
        state.setdefault("expressed_skills", []).append(skill)
        state["expressed_skills"] = state["expressed_skills"][-20:]
        # Write skill to disk — the organism literally births a skill
        skill_path = _write_skill_to_disk(skill)
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "express", "ok": True, "skill": skill, "skill_path": skill_path}

    if action == "propagate":
        result = _propagate(state.get("mutations", []), modules)
        return {"wave": WAVE, "name": NAME, "action": "propagate", "ok": True, **result}

    if action == "canvas":
        mutations = state.get("mutations", [])
        paradigm_counts = {}
        for m in mutations:
            p = m.get("paradigm", "unknown")
            paradigm_counts[p] = paradigm_counts.get(p, 0) + 1
        
        return {"wave": WAVE, "name": NAME, "action": "canvas", "ok": True,
                "total_mutations": len(mutations),
                "paradigm_distribution": paradigm_counts,
                "module_count": len(modules),
                "skills_expressed": len(state.get("expressed_skills", []))}

    if action == "full_cycle":
        # One complete cycle: mutate -> express -> propagate
        # Mutate
        donors = list(profiles.keys()) if profiles else ["wave734_repo_dna", "wave751_evolution_kernel"]
        child = _mutate_dna(profiles.get(donors[0], {}), profiles.get(donors[1] if len(donors) > 1 else 0, {}))
        state.setdefault("mutations", []).append(child)
        
        # Express
        skill = _express_skill_from_dna(child)
        state.setdefault("expressed_skills", []).append(skill)
        skill_path = _write_skill_to_disk(skill)
        
        # Propagate
        prop = _propagate(state["mutations"], modules)
        
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "full_cycle", "ok": True,
                "mutation": child, "skill": skill, "skill_path": skill_path, "propagation": prop}

    return {"wave": WAVE, "name": NAME, "action": action, "ok": False, "error": "unknown_action"}


def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "active",
            "resonance": 0.79, "mutations": len(state.get("mutations", []))}


def resonates_with() -> list:
    return ["gene_splicer", "repo_dna_skill", "skill_builder", "evolution_kernel"]
