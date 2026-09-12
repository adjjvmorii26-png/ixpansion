"""Knowledge Garden Auto-Expansion System.
Auto-expands the knowledge garden by discovering new modules from cross-pollination,
categorizing modules by domain, and managing expiry/refresh based on activity."""
import json
import time
import os
import random
from typing import Dict, List, Optional, Any
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Module categories for the garden
_MODULE_CATEGORIES = {
    "entropy": ["entropy_weather", "entropy_weaver", "entropy_oracle", "chaos_reactor"],
    "dream": ["dream_journal", "dream_logic_physics", "dream_branch", "prophecy_engine"],
    "resonance": ["coherence_resonator", "resonance_chord", "resonance_topology", "echo_symphony"],
    "coherence": ["coherence_regulator", "coherence_vitals", "coherence_weaver", "phase_transition"],
    "agent": ["agent_fabricator", "spectral_agent", "synthetic_agent", "overseer_agent"],
    "wave": ["wave_orchestrator", "wave_timeline", "wave_summoner", "generation_profiles"],
    "memory": ["memory_garden_tender", "memory_weaver", "memory_crystal_forge", "dreams"],
    "cross_pollination": ["cross_pollination", "module_search", "pattern_mining", "repo_traversal"],
    "naming": ["autonomous_naming", "naming_ceremony", "module_name_generator"],
    "visualization": ["resonance_graph", "vibe_dashboard", "depth_visualizer", "topology_visualizer"]
}

# Auto-expansion configuration
_EXPANSION_CONFIG = {
    "enabled": True,
    "max_modules_per_category": 20,
    "expiry_days": 30,
    "refresh_threshold_days": 7,
    "discovery_interval_hours": 6,
    "max_total_modules": 200
}

# Garden state
_garden_state = {
    "modules": {},  # module_name -> {category, last_active, times_refreshed, status}
    "categories": {cat: [] for cat in _MODULE_CATEGORIES},
    "expansion_history": [],
    "last_discovery": None,
    "total_modules": 0
}


def categorize_module(module_name: str) -> str:
    """Categorize a module based on its name."""
    name_lower = module_name.lower()
    
    for category, patterns in _MODULE_CATEGORIES.items():
        for pattern in patterns:
            if pattern in name_lower or name_lower in pattern:
                return category
    
    # Fallback: check for keywords
    if "entropy" in name_lower or "chaos" in name_lower:
        return "entropy"
    elif "dream" in name_lower or "lucid" in name_lower:
        return "dream"
    elif "resonance" in name_lower or "coherence" in name_lower:
        return "resonance"
    elif "agent" in name_lower:
        return "agent"
    elif "wave" in name_lower or "generation" in name_lower:
        return "wave"
    elif "memory" in name_lower or "dream" in name_lower:
        return "memory"
    elif "cross" in name_lower or "pollination" in name_lower or "pattern" in name_lower:
        return "cross_pollination"
    elif "naming" in name_lower or "ceremony" in name_lower:
        return "naming"
    elif "visual" in name_lower or "dashboard" in name_lower or "graph" in name_lower:
        return "visualization"
    
    return "uncategorized"


def discover_new_modules() -> List[str]:
    """Discover new modules from cross-pollination scan."""
    try:
        from api.skill_injection import inject_skill
        from api.emergent_skills import invoke_skill
        
        # Inject cross_pollination if needed
        inject_skill("cross_pollination")
        
        # Scan for patterns
        result = invoke_skill("cross_pollination", "scan_repo_patterns", 
                            repo_path=str(Path(__file__).resolve().parents[1]))
        
        new_modules = []
        for opp in result.get("opportunities", []):
            for cls in opp.get("classes", []):
                module_name = f"auto_{cls.lower()}"
                if module_name not in _garden_state["modules"]:
                    new_modules.append(module_name)
            
            for func in opp.get("functions", []):
                module_name = f"auto_{func.lower()}"
                if module_name not in _garden_state["modules"]:
                    new_modules.append(module_name)
        
        return new_modules[:10]  # Limit discoveries
    except Exception:
        return []


def auto_expand_garden() -> dict:
    """Auto-expand the garden with discovered modules."""
    if not _EXPANSION_CONFIG["enabled"]:
        return {"status": "disabled", "message": "Auto-expansion not enabled"}
    
    # Check total module limit
    if _garden_state["total_modules"] >= _EXPANSION_CONFIG["max_total_modules"]:
        return {"status": "limit_reached", "total_modules": _garden_state["total_modules"]}
    
    # Discover new modules
    new_modules = discover_new_modules()
    
    added = []
    for module_name in new_modules:
        category = categorize_module(module_name)
        
        # Check category limit
        if len(_garden_state["categories"].get(category, [])) >= _EXPANSION_CONFIG["max_modules_per_category"]:
            continue
        
        # Add to garden
        _garden_state["modules"][module_name] = {
            "category": category,
            "last_active": time.time(),
            "times_refreshed": 0,
            "status": "living",
            "discovered_at": time.time()
        }
        _garden_state["categories"].setdefault(category, []).append(module_name)
        _garden_state["total_modules"] += 1
        added.append(module_name)
    
    # Record expansion
    _garden_state["expansion_history"].append({
        "timestamp": time.time(),
        "modules_added": added,
        "count": len(added)
    })
    _garden_state["last_discovery"] = time.time()
    
    return {
        "status": "expanded",
        "modules_added": added,
        "count": len(added),
        "total_modules": _garden_state["total_modules"]
    }


def refresh_module(module_name: str) -> dict:
    """Refresh a module's activity timestamp."""
    if module_name in _garden_state["modules"]:
        _garden_state["modules"][module_name]["last_active"] = time.time()
        _garden_state["modules"][module_name]["times_refreshed"] += 1
        _garden_state["modules"][module_name]["status"] = "living"
        
        return {
            "status": "refreshed",
            "module": module_name,
            "times_refreshed": _garden_state["modules"][module_name]["times_refreshed"]
        }
    
    return {"status": "not_found", "module": module_name}


def check_expiries() -> dict:
    """Check for expired modules and update their status."""
    now = time.time()
    expiry_threshold = _EXPANSION_CONFIG["expiry_days"] * 24 * 3600
    refresh_threshold = _EXPANSION_CONFIG["refresh_threshold_days"] * 24 * 3600
    
    expired = []
    need_refresh = []
    living = []
    
    for module_name, info in _garden_state["modules"].items():
        age = now - info.get("last_active", now)
        
        if age > expiry_threshold:
            info["status"] = "expired"
            expired.append(module_name)
        elif age > refresh_threshold:
            info["status"] = "needs_refresh"
            need_refresh.append(module_name)
        else:
            info["status"] = "living"
            living.append(module_name)
    
    return {
        "living": living,
        "need_refresh": need_refresh,
        "expired": expired,
        "total": len(_garden_state["modules"])
    }


def get_garden_status() -> dict:
    """Get comprehensive garden status."""
    expiry_info = check_expiries()
    
    # Category breakdown
    category_stats = {}
    for cat, modules in _garden_state["categories"].items():
        living = sum(1 for m in modules if _garden_state["modules"].get(m, {}).get("status") == "living")
        category_stats[cat] = {
            "total": len(modules),
            "living": living,
            "modules": modules[:10]  # Limit display
        }
    
    return {
        "total_modules": _garden_state["total_modules"],
        "expansion_enabled": _EXPANSION_CONFIG["enabled"],
        "categories": category_stats,
        "expiry_check": {
            "living": len(expiry_info["living"]),
            "need_refresh": len(expiry_info["need_refresh"]),
            "expired": len(expiry_info["expired"])
        },
        "last_discovery": _garden_state["last_discovery"],
        "expansion_history": _garden_state["expansion_history"][-5:],
        "config": _EXPANSION_CONFIG
    }


def enable_expansion(enabled: bool = True) -> dict:
    """Enable/disable auto-expansion."""
    _EXPANSION_CONFIG["enabled"] = enabled
    return {"status": "enabled" if enabled else "disabled", "config": _EXPANSION_CONFIG}


# CLI entry point
if __name__ == "__main__":
    import argparse
    import json as _json
    
    parser = argparse.ArgumentParser(description="Knowledge Garden Auto-Expansion")
    parser.add_argument("--expand", action="store_true", help="Trigger auto-expansion")
    parser.add_argument("--status", action="store_true", help="Get garden status")
    parser.add_argument("--refresh", type=str, help="Refresh a module")
    parser.add_argument("--check", action="store_true", help="Check expiries")
    parser.add_argument("--enable", action="store_true", help="Enable auto-expansion")
    parser.add_argument("--disable", action="store_true", help="Disable auto-expansion")
    parser.add_argument("--categorize", type=str, help="Categorize a module name")
    
    args = parser.parse_args()
    
    if args.expand:
        result = auto_expand_garden()
        print(f"Expansion: {_json.dumps(result, indent=2)}")
    
    if args.status:
        result = get_garden_status()
        print(f"Garden Status: {_json.dumps(result, indent=2)}")
    
    if args.refresh:
        result = refresh_module(args.refresh)
        print(f"Refresh: {_json.dumps(result)}")
    
    if args.check:
        result = check_expiries()
        print(f"Expiry Check: {_json.dumps(result, indent=2)}")
    
    if args.enable:
        result = enable_expansion(True)
        print(f"Expansion: {_json.dumps(result)}")
    
    if args.disable:
        result = enable_expansion(False)
        print(f"Expansion: {_json.dumps(result)}")
    
    if args.categorize:
        result = categorize_module(args.categorize)
        print(f"Category: {result}")
    
    if not any([args.expand, args.status, args.refresh, args.check, args.enable, args.disable, args.categorize]):
        print("Knowledge Garden Auto-Expansion operational")
        print("Commands: --expand, --status, --refresh <module>, --check, --enable, --disable, --categorize <name>")
