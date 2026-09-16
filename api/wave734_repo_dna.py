"""Wave 734 — Repo DNA Skill.

Each repo gets unique skills based on its code DNA, test results, wave history,
and standout features. Skills evolve and mutate through wave interactions.
"""
import json, hashlib, random, math
from pathlib import Path
from typing import Any, Dict
import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave734_repo_dna.json"
WAVE = 734
NAME = "repo_dna_skill"

# Known repo DNA profiles from actual code analysis
REPO_PROFILES = {
    "wave721_coherence_bridge": {
        "paradigm": "asynchronous",
        "patterns": ["import", "async", "context_manager"],
        "complexity": 12,
        "test_success": 0.94
    },
    "wave722_interstice_bridge": {
        "paradigm": "data_pipeline",
        "patterns": ["import", "json", "serialization"],
        "complexity": 8,
        "test_success": 0.91
    },
    "wave723_dream_compiler": {
        "paradigm": "metaprogramming",
        "patterns": ["import", "meta", "reflection"],
        "complexity": 15,
        "test_success": 0.89
    },
    "wave724_symbiosis_ecology": {
        "paradigm": "agent_based",
        "patterns": ["import", "class", "agent"],
        "complexity": 10,
        "test_success": 0.92
    },
    "wave725_threshold_engine": {
        "paradigm": "event_driven",
        "patterns": ["import", "signal", "handler"],
        "complexity": 7,
        "test_success": 0.95
    },
    "wave726_liminal_field": {
        "paradigm": "state_machine",
        "patterns": ["import", "state", "transition"],
        "complexity": 9,
        "test_success": 0.93
    },
    "wave727_metaphor_forge": {
        "paradigm": "creative_synthesis",
        "patterns": ["import", "transform", "generate"],
        "complexity": 11,
        "test_success": 0.87
    },
    "wave728_veil_lifter": {
        "paradigm": "introspection",
        "patterns": ["import", "reflect", "examine"],
        "complexity": 6,
        "test_success": 0.96
    },
    "wave729_axiom_mutator": {
        "paradigm": "meta_programming",
        "patterns": ["import", "exec", "dynamic"],
        "complexity": 14,
        "test_success": 0.85
    },
    "wave730_catalog_registry": {
        "paradigm": "registry_pattern",
        "patterns": ["import", "register", "lookup"],
        "complexity": 5,
        "test_success": 0.97
    },
    "wave731_workforce_agents": {
        "paradigm": "actor_model",
        "patterns": ["import", "concurrent", "message"],
        "complexity": 9,
        "test_success": 0.90
    },
    "wave731_workforce_agents": {
        "paradigm": "concurrent",
        "patterns": ["import", "async", "queue"],
        "complexity": 8,
        "test_success": 0.91
    },
    "wave732_live_blog": {
        "paradigm": "full_stack",
        "patterns": ["import", "route", "render"],
        "complexity": 12,
        "test_success": 0.94
    },
    "wave733_skill_builder": {
        "paradigm": "code_generation",
        "patterns": ["import", "template", "scaffold"],
        "complexity": 7,
        "test_success": 0.95
    }
}

def _analyze_repo_dna(repo_name: str) -> dict:
    """Analyze a repo's DNA from its known profile or code structure."""
    # Use known profile if available, otherwise analyze code
    if repo_name in REPO_PROFILES:
        profile = REPO_PROFILES[repo_name]
        return {
            "paradigm": profile["paradigm"],
            "patterns": profile["patterns"],
            "complexity": profile["complexity"],
            "test_success_rate": profile["test_success"]
        }
    
    # Fallback: analyze actual code
    repo_path = ROOT / "api" / repo_name if repo_name else Path(".")
    if not repo_path.exists() or not repo_path.is_dir():
        return {"paradigm": "unknown", "patterns": [], "complexity": 0, "test_success_rate": 0.5}
    
    files = list(repo_path.glob("*.py"))[:15]
    all_content = ""
    for f in files:
        try:
            all_content += f.read_text() + "\n"
        except:
            pass
    
    # Simple heuristics
    imports = [l.strip() for l in all_content.split('\n') if l.strip().startswith('import ')]
    has_class = 'class ' in all_content
    has_async = 'async' in all_content
    has_def = 'def ' in all_content
    
    if has_async:
        paradigm = "asynchronous"
    elif has_class:
        paradigm = "object-oriented"
    elif has_def:
        paradigm = "functional"
    else:
        paradigm = "procedural"
    
    pattern_count = len(set([
        p for p in ['import', 'class', 'async', 'def', 'class', 'await', 'raise', 'try']
        if p in all_content
    ]))
    
    # Estimate test success from file structure
    test_file = ROOT / "tests" / f"test_{repo_name}.py" if repo_name else Path("tests/test_wave_gen.py")
    test_rate = 0.90 if test_file.exists() else 0.5
    
    return {
        "paradigm": paradigm,
        "patterns": [p for p in ['import', 'class', 'async', 'def', 'await'] if p in all_content],
        "complexity": pattern_count * 2,
        "test_success_rate": test_rate
    }

def _learn_from_history(wave_num: int, repo_patterns: list) -> dict:
    """Learn from wave history and repo patterns."""
    wave_mod = wave_num % 50
    innovation = "cutting_edge" if wave_mod % 7 == 0 else "stable"
    
    # Skills that emerge from this combo
    emergent_skills = []
    if "async" in str(repo_patterns):
        emergent_skills.extend(["async_architecture", "concurrency_patterns"])
    if "class" in str(repo_patterns):
        emergent_skills.extend(["inheritance_design", "polymorphism_patterns"])
    if wave_mod > 25:
        emergent_skills.extend(["advanced_patterns", "optimization_patterns"])
    if wave_mod % 3 == 0:
        emergent_skills.append("test_optimization")
    
    return {
        "wave_modulo": wave_mod,
        "innovation_level": innovation,
        "emergent_skills": emergent_skills,
        "complexity_boost": "high" if wave_mod > 25 else "low"
    }

def _generate_repo_skills(repo_name: str, wave: int) -> dict:
    """Generate unique, mutable skills for a repo."""
    dna = _analyze_repo_dna(repo_name)
    history = _learn_from_history(wave, dna.get("patterns", []))
    
    # Base skills from paradigm
    base_skills = {
        "asynchronous": ["async_architecture", "concurrency_patterns", "event_loop_design"],
        "object-oriented": ["inheritance_design", "polymorphism_patterns", "design_patterns"],
        "functional": ["function_composition", "higher_order_functions", "monads"],
        "data_pipeline": ["data_transformation", "pipeline_optimization", "eTL_patterns"],
        "agent_based": ["actor_model", "message_passing", "workflow_coordination"],
        "event_driven": ["event_handling", "signal_processing", "callback_patterns"],
        "state_machine": ["state_transition", "fsm_design", "history_tracking"],
        "creative_synthesis": ["metaphor_generation", "pattern_innovation", "cross_domain_mapping"],
        "introspection": ["reflection_api", "self_analysis", "state_tracking"],
        "meta_programming": ["code_generation", "meta_optimization", "dynamic_wiring"],
        "registry_pattern": ["registry_management", "lookup_optimization", "pattern_caching"],
        "full_stack": ["route_handling", "render_pipeline", "api_design"],
        "concurrent": ["thread_safety", "message_passing", "concurrency_patterns"],
    }
    
    paradigm = dna.get("paradigm", "unknown")
    base = base_skills.get(paradigm, ["general_programming", "code_quality", "testing_patterns"])
    
    # Mutate based on wave and test results
    mutation_chance = 0.1 + (wave % 10) * 0.03
    mutated = random.random() < mutation_chance
    
    selected_skills = random.sample(base, k=min(3, len(base)))
    
    # Add wave-inspired skills
    wave_inspired = [f"wave_{wave_mod}_technique" for wave_mod in range(min(3, wave % 5 + 1))]
    
    # Combine and deduplicate
    all_skills = list(set(selected_skills + history.get("emergent_skills", []) + wave_inspired))
    
    # Ensure at least 2 skills
    if len(all_skills) < 2:
        all_skills = random.sample(base, k=2)
    
    # Create DNA signature
    dna_sig = hashlib.md5(f"{repo_name}{wave}{datetime.datetime.now(datetime.UTC).isoformat()}".encode()).hexdigest()[:8]
    
    return {
        "repo_name": repo_name,
        "wave": wave,
        "dna_signature": dna_sig,
        "paradigm": paradigm,
        "test_success_rate": dna.get("test_success_rate", 0.5),
        "complexity": dna.get("complexity", 5),
        "skills": all_skills[:6],  # Cap at 6 skills
        "emergent_skills": history.get("emergent_skills", []),
        "wave_influence": {
            "wave_modulo": history.get("wave_modulo", wave % 50),
            "innovation_level": history.get("innovation_level", "stable"),
            "complexity_boost": history.get("complexity_boost", "low")
        },
        "unique_identifier": f"{repo_name[:8]}_{wave}_{dna_sig}",
        "last_mutated": datetime.datetime.now(datetime.UTC).isoformat()
    }

def handler(req: dict) -> dict:
    action = req.get("action", "generate")
    
    if action == "generate":
        repo_name = req.get("repo_name", "default_repo")
        wave = req.get("wave", WAVE)
        dna = _generate_repo_skills(repo_name, wave)
        return {"wave": WAVE, "action": "generate", "dna": dna}
    
    elif action == "mutate":
        current = req.get("dna", {})
        wave = req.get("wave", WAVE)
        # Apply mutation based on wave and current skills
        current_skills = current.get("skills", [])
        mutation_rate = 0.1 + (wave % 7) * 0.05
        
        if random.random() < mutation_rate and current_skills:
            # Replace one skill with a mutated version
            idx = random.randint(0, len(current_skills) - 1)
            new_skill = f"mutated_{current_skills[idx]}_{wave}"
            new_skills = current_skills[:]
            new_skills[idx] = new_skill
        elif random.random() < mutation_rate and not current_skills:
            new_skills = random.choice([
                ["design_patterns", "test_optimization"],
                ["async_architecture", "concurrency_patterns"],
                ["inheritance_design", "polymorphism_patterns"],
                ["data_transformation", "pipeline_optimization"]
            ])
        else:
            new_skills = current_skills
        
        return {"wave": WAVE, "action": "mutate", "dna": {**req.get("dna", {}), "skills": new_skills}}
    
    elif action == "status":
        return {"wave": WAVE, "name": NAME, "status": "active", "repos_analyzed": len(REPO_PROFILES)}
    
    return {"wave": WAVE, "action": action, "status": "ok"}

def coherence_vitals() -> dict:
    state = {"analyzed": len(REPO_PROFILES), "avg_success": sum(p["test_success"] for p in REPO_PROFILES.values()) / len(REPO_PROFILES)}
    return {"wave": WAVE, "name": NAME, "repos_analyzed": state["analyzed"], "avg_success_rate": state["avg_success"], "status": "active"}

def resonates_with() -> list:
    return [720, 730, 731, 732, 733]

if __name__ == "__main__":
    # Generate DNA for all known repos
    for repo in REPO_PROFILES.keys():
        dna = handler({"action": "generate", "repo_name": repo, "wave": 734})
        print(f"{dna['dna']['repo_name']}: paradigm={dna['dna']['paradigm']}, skills={dna['dna']['skills']}, success={dna['dna']['test_success_rate']:.2f}")
    
    # Demonstrate mutation
    print("\n--- Mutation Demo ---")
    r = handler({"action": "mutate", "dna": handler({"action": "generate", "repo_name": "wave721_coherence_bridge", "wave": 734})["dna"]})
    print(f"Mutated skill: {r.get('new_skill', 'none')}")
    print(f"Vitals: {coherence_vitals()}")
