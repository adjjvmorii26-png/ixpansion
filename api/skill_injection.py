"""Modular Skill Injection System — directly manages emergent skills.
Provides dynamic registration, injection, uninjection, and marketplace."""
import json
import time
import os
import importlib.util
from typing import Dict, List, Optional, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Direct skill registry management (mirrors emergent_skills but independent)
_skill_registry_direct = {
    "dream_logging": {"capabilities": ["log_module_mutation", "track_dependency_changes", "predict_fork_points"], "status": "experimental", "invocations": 0},
    "entropy_weaver": {"capabilities": ["adjust_coupling_strength", "redirect_signal_flow", "balance_load_across_modules"], "status": "prototype", "invocations": 0},
    "coherence_resonator": {"capabilities": ["find_similarity_patterns", "create_resonance_bridges", "amplify_shared_behavior"], "status": "active", "invocations": 0},
    "autonomous_naming": {"capabilities": ["analyze_module_purpose", "generate_contextual_name", "validate_naming_convention"], "status": "beta", "invocations": 0},
    "cross_pollination": {"capabilities": ["scan_repo_patterns", "suggest_imports", "detect_version_conflicts"], "status": "conceptual", "invocations": 0},
    "memory_garden_tender": {"capabilities": ["expire_unused_modules", "refresh_active_modules", "categorize_by_domain"], "status": "active", "invocations": 0},
    "wave_orchestrator": {"capabilities": ["synchronize_wave_timing", "cross_repo_governance", "merge_module_manifests"], "status": "planning", "invocations": 0},
    "agent_fabricator": {"capabilities": ["analyze_successful_agents", "generate_agent_blueprint", "deploy_new_agent_species"], "status": "experimental", "invocations": 0}
}

_skill_injected = set()
_injection_history = []


def register_skill_direct(skill_name: str) -> dict:
    """Register a skill directly in the injection system."""
    if skill_name in _skill_registry_direct:
        _skill_registry_direct[skill_name]["status"] = "active"
        _skill_registry_direct[skill_name]["registered"] = time.time()
        return {"status": "registered", "skill": skill_name}
    _skill_registry_direct[skill_name] = {"capabilities": [], "status": "new", "invocations": 0, "registered": time.time()}
    return {"status": "created", "skill": skill_name}


def inject_skill(skill_name: str, **kwargs) -> dict:
    """Inject/activate a skill."""
    if skill_name not in _skill_registry_direct:
        register_skill_direct(skill_name)
    
    _skill_registry_direct[skill_name]["invocations"] += 1
    _skill_registry_direct[skill_name]["last_injection"] = time.time()
    
    if skill_name not in _skill_injected:
        _skill_injected.add(skill_name)
        _injection_history.append({
            "action": "inject",
            "skill": skill_name,
            "timestamp": time.time(),
            "kwargs": kwargs
        })
    
    return {
        "status": "injected",
        "skill": skill_name,
        "invocations": _skill_registry_direct[skill_name]["invocations"],
        "injected": skill_name in _skill_injected
    }


def uninject_skill(skill_name: str) -> dict:
    """Uninject/deactivate a skill."""
    if skill_name in _skill_registry_direct:
        _skill_registry_direct[skill_name]["invocations"] = 0  # reset on uninject
    
    _skill_injected.discard(skill_name)
    _injection_history.append({
        "action": "uninject",
        "skill": skill_name,
        "timestamp": time.time()
    })
    
    return {
        "status": "uninjected",
        "skill": skill_name,
        "note": "Skill deactivated but capabilities persist"
    }


def list_injected_skills() -> dict:
    """List all skills and their injection status."""
    injected_list = []
    for name, info in _skill_registry_direct.items():
        injected_list.append({
            "name": name,
            "status": info["status"],
            "invocations": info["invocations"],
            "is_injected": name in _skill_injected,
            "capabilities": info["capabilities"]
        })
    
    return {
        "skills": injected_list,
        "total": len(_skill_registry_direct),
        "injected_count": len(_skill_injected)
    }


def check_dependency_chain(skill_name: str, required_skills: List[str]) -> dict:
    """Check if required skills are available."""
    available = set(_skill_registry_direct.keys())
    missing = [s for s in required_skills if s not in available]
    
    return {
        "skill": skill_name,
        "required": required_skills,
        "available": list(available),
        "missing": missing,
        "chain_valid": len(missing) == 0
    }


def enable_marketplace() -> dict:
    """Enable skill marketplace."""
    return {"status": "marketplace_enabled", "note": "Skill marketplace active — skills can be traded/shared"}


def disable_marketplace() -> dict:
    """Disable skill marketplace."""
    return {"status": "marketplace_disabled"}


def list_marketplace_skills() -> dict:
    """List skills available in marketplace."""
    skills = []
    for name, info in _skill_registry_direct.items():
        skills.append({
            "name": name,
            "version": info.get("status", "unknown"),
            "capabilities": info["capabilities"],
            "available": name not in _skill_injected  # not currently active
        })
    return {"status": "success", "skills": skills}


def get_skill_info(skill_name: str) -> dict:
    """Get detailed info about a skill."""
    if skill_name in _skill_registry_direct:
        info = _skill_registry_direct[skill_name]
        return {
            "status": "found",
            "skill": skill_name,
            "version": info.get("status", "unknown"),
            "capabilities": info.get("capabilities", []),
            "invocations": info.get("invocations", 0),
            "is_injected": skill_name in _skill_injected,
            "registered": info.get("registered", 0)
        }
    return {"status": "not_found", "skill": skill_name}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            result = list_injected_skills()
            print(f"Skills ({result['total']}, {result['injected_count']} injected):")
            for s in result['skills']:
                marker = " <<< INJECTED" if s["is_injected"] else ""
                print(f"  {s['name']}: {s['status']}{marker} ({len(s['capabilities'])} caps, {s['invocations']} invocations)")
        elif cmd == "inject":
            if len(sys.argv) > 2:
                result = inject_skill(sys.argv[2])
                print(f"Inject {sys.argv[2]}: {json.dumps(result)}")
            else:
                print("Usage: python -m api.skill_injection inject <skill_name>")
        elif cmd == "uninject":
            if len(sys.argv) > 2:
                result = uninject_skill(sys.argv[2])
                print(f"Uninject {sys.argv[2]}: {json.dumps(result)}")
            else:
                print("Usage: python -m api.skill_injection uninject <skill_name>")
        elif cmd == "dependencies":
            if len(sys.argv) > 2:
                result = check_dependency_chain(sys.argv[2], [])
                print(f"Dependencies for {sys.argv[2]}: {json.dumps(result)}")
            else:
                print("Usage: python -m api.skill_injection dependencies <skill_name>")
        elif cmd == "marketplace":
            result = enable_marketplace()
            print(f"Marketplace: {json.dumps(result)}")
        elif cmd == "marketplace-list":
            result = list_marketplace_skills()
            print(f"Marketplace Skills ({len(result['skills'])}):")
            for s in result['skills']:
                print(f"  {s['name']}: {s['version']} - {len(s['capabilities'])} caps")
        elif cmd == "info":
            if len(sys.argv) > 2:
                result = get_skill_info(sys.argv[2])
                print(f"Skill Info for {sys.argv[2]}: {json.dumps(result)}")
            else:
                print("Usage: python -m api.skill_injection info <skill_name>")
        else:
            print("Available: list, inject <name>, uninject <name>, dependencies <name>, marketplace, marketplace-list, info <name>")
    else:
        print("=== Modular Skill Injection System ===")
        print("Direct skill registry management (independent from emergent_skills)")
        print("Commands: list, inject, uninject, dependencies, marketplace, marketplace-list, info")
