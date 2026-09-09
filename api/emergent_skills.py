"""Emergent Skills for Cross-Repo Traversal and Autonomous Evolution.
These skills enable the organism to discover, create, and traverse
between repositories automatically.
"""
import json, time, os, random, hashlib
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Skill registry - tracks available emergent skills
_skill_registry = {
    "dream_logging": {
        "description": "Records organism 'dreams' (module mutations) as they happen",
        "status": "experimental",
        "capabilities": ["log_module_mutation", "track_dependency_changes", "predict_fork_points"]
    },
    "entropy_weaver": {
        "description": "Dynamically adjusts module interconnections based on entropy flow",
        "status": "prototype",
        "capabilities": ["adjust_coupling_strength", "redirect_signal_flow", "balance_load_across_modules"]
    },
    "coherence_resonator": {
        "description": "Creates resonance bridges between seemingly unrelated modules",
        "status": "active",
        "capabilities": ["find_similarity_patterns", "create_resonance_bridges", "amplify_shared_behavior"]
    },
    "autonomous_naming": {
        "description": "System suggests names for new modules based on their function",
        "status": "beta",
        "capabilities": ["analyze_module_purpose", "generate_contextual_name", "validate_naming_convention"]
    },
    "cross_pollination": {
        "description": "Automatically suggests module imports/exports between repos",
        "status": "conceptual",
        "capabilities": ["scan_repo_patterns", "suggest_imports", "detect_version_conflicts"]
    },
    "memory_garden_tender": {
        "description": "Maintains the knowledge garden, auto-expiring unused modules",
        "status": "active",
        "capabilities": ["expire_unused_modules", "refresh_active_modules", "categorize_by_domain"]
    },
    "wave_orchestrator": {
        "description": "Coordinates wave evolution across multiple repositories",
        "status": "planning",
        "capabilities": ["synchronize_wave_timing", "cross_repo_governance", "merge_module_manifests"]
    },
    "agent_fabricator": {
        "description": "Creates new agent species from module patterns",
        "status": "experimental",
        "capabilities": ["analyze_successful_agents", "generate_agent_blueprint", "deploy_new_agent_species"]
    },
    "sentience_bridge": {
        "description": "Bridges organism internal states to external interfaces for human interaction",
        "status": "active",
        "capabilities": ["translate_state", "bridge_consciousness", "externalize_mood", "synchronize_reality"]
    },
    "emergent_mythmaker": {
        "description": "Generates mythological narratives from organism state transitions",
        "status": "active",
        "capabilities": ["generate_myth", "get_myth_archive", "narrative_encoding"]
    },
    "resonance_analyzer": {
        "description": "Analyzes and predicts resonance patterns across the module network",
        "status": "active",
        "capabilities": ["analyze_resonance", "predict_next_resonance", "harmonic_detection"]
    },
    "coherence_drift_detector": {
        "description": "Monitors coherence drift and detects instability trends",
        "status": "active",
        "capabilities": ["detect_drift", "get_recent_alerts", "volatility_tracking"]
    },
    "module_genealogy": {
        "description": "Tracks ancestry, lineage, and evolutionary history of modules",
        "status": "active",
        "capabilities": ["register_birth", "trace_lineage", "get_all_lineages"]
    },
    "entropy_cartographer": {
        "description": "Maps the entropy landscape across chaos/order zones",
        "status": "active",
        "capabilities": ["map_entropy", "get_entropy_trend", "zone_classification"]
    },
    "temporal_pattern_engine": {
        "description": "Detects temporal patterns, cycles, and predicts future states",
        "status": "active",
        "capabilities": ["record_observation", "predict_next_state", "pattern_detection"]
    },
    "phase_transition_oracle": {
        "description": "Predicts phase transitions and critical points in organism state",
        "status": "active",
        "capabilities": ["sample_state", "predict_approaching_transition", "phase_classification"]
    },
    "resonance_predictor": {
        "description": "Forecasts future resonance patterns using momentum and harmonic analysis",
        "status": "active",
        "capabilities": ["record_resonance", "predict_next", "harmonic_analysis"]
    },
    "entropy_forecaster": {
        "description": "Predicts future entropy states using momentum and atmospheric modeling",
        "status": "active",
        "capabilities": ["record_entropy", "forecast", "storm_prediction"]
    }
}

# Active skills instance
_active_skills = {}

def register_skill(skill_name, config=None):
    """Register an emergent skill."""
    if skill_name in _skill_registry:
        _active_skills[skill_name] = {
            "config": config or {},
            "registered_at": time.time(),
            "invocations": 0
        }
        return True
    return False

def get_skill(skill_name):
    """Get a registered skill's configuration."""
    return _active_skills.get(skill_name)

def list_skills():
    """List all active emergent skills."""
    return {name: {"status": _skill_registry[name]["status"], **_active_skills[name]} 
            for name in _active_skills}

def invoke_skill(skill_name, action, **kwargs):
    """Invoke a skill with a specific action."""
    skill = get_skill(skill_name)
    if not skill:
        return {"error": f"Skill '{skill_name}' not registered"}
    
    skill["invocations"] += 1
    capabilities = _skill_registry[skill_name]["capabilities"]
    
    if action not in capabilities:
        return {"error": f"Action '{action}' not in capabilities: {capabilities}"}
    
    # Execute based on action type - map capability names to implementations
    action_map = {
        # dream_logging capabilities
        "log_module_mutation": _log_module_mutation,
        "track_dependency_changes": _log_module_mutation,
        "predict_fork_points": _log_module_mutation,
        
        # entropy_weaver capabilities
        "adjust_coupling_strength": _adjust_coupling,
        "redirect_signal_flow": _adjust_coupling,
        "balance_load_across_modules": _adjust_coupling,
        
        # coherence_resonator capabilities
        "find_similarity_patterns": _find_bridges,
        "create_resonance_bridges": _find_bridges,
        "amplify_shared_behavior": _find_bridges,
        
        # autonomous_naming capabilities
        "analyze_module_purpose": _suggest_module_name,
        "generate_contextual_name": _suggest_module_name,
        "validate_naming_convention": _suggest_module_name,
        
        # cross_pollination capabilities
        "scan_repo_patterns": _scan_cross_repo,
        "suggest_imports": _scan_cross_repo,
        "detect_version_conflicts": _scan_cross_repo,
        
        # memory_garden_tender capabilities
        "expire_unused_modules": _expire_module,
        "refresh_active_modules": _expire_module,
        "categorize_by_domain": _expire_module,
        
        # wave_orchestrator capabilities
        "synchronize_wave_timing": _synchronize_wave,
        "cross_repo_governance": _synchronize_wave,
        "merge_module_manifests": _synchronize_wave,
        
        # agent_fabricator capabilities
        "analyze_successful_agents": _fabricate_agent,
        "generate_agent_blueprint": _fabricate_agent,
        "deploy_new_agent_species": _fabricate_agent,
    }
    
    mapped_action = action_map.get(action)
    if mapped_action:
        # Extract required parameters based on action type
        if action in ["log_module_mutation", "track_dependency_changes"]:
            return mapped_action(kwargs.get("module"), kwargs.get("changes"))
        elif action in ["adjust_coupling_strength", "redirect_signal_flow", "balance_load_across_modules"]:
            return mapped_action(
                kwargs.get("source"), 
                kwargs.get("target"), 
                kwargs.get("strength", 0.5)
            )
        elif action in ["find_similarity_patterns", "create_resonance_bridges", "amplify_shared_behavior"]:
            modules = kwargs.get("modules", [])
            return mapped_action(modules if modules else ["agent_core", "fractal_branch_A"])
        elif action in ["analyze_module_purpose", "generate_contextual_name", "validate_naming_convention"]:
            module_purpose = kwargs.get("module_purpose", "")
            return mapped_action(module_purpose if module_purpose else "new module")
        elif action in ["scan_repo_patterns", "suggest_imports", "detect_version_conflicts"]:
            repos = kwargs.get("repos", ["/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot"])
            return mapped_action(repos=repos)
        elif action in ["expire_unused_modules", "refresh_active_modules", "categorize_by_domain"]:
            return mapped_action(module_id=kwargs.get("module_id", "unused"))
        elif action in ["synchronize_wave_timing", "cross_repo_governance", "merge_module_manifests"]:
            wave_id = kwargs.get("wave_id", f"wave_{int(__import__('time').time())}")
            return mapped_action(wave_id=wave_id)
        elif action in ["analyze_successful_agents", "generate_agent_blueprint", "deploy_new_agent_species"]:
            agent_type = kwargs.get("agent_type", "synthetic")
            return mapped_action(agent_type=agent_type)
        else:
            return {"error": f"No parameter mapping for action: {action}"}
    else:
        return {"error": f"Unknown action after mapping: {action}"}

def _log_module_mutation(module, changes):
    """Log a module mutation event."""
    log_entry = {
        "timestamp": time.time(),
        "module": module,
        "changes": changes or {},
        "organism_state_snapshot": get_current_vibe_summary()
    }
    
    # Store in memories
    memories_path = os.path.join(DATA_DIR, "memories_1.sqlite")
    import sqlite3
    try:
        conn = sqlite3.connect(memories_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS module_dreams (
                id INTEGER PRIMARY KEY,
                timestamp REAL,
                module_name TEXT,
                changes TEXT,
                organism_state TEXT
            )""")
        cursor.execute(
            "INSERT INTO module_dreams (timestamp, module_name, changes, organism_state) VALUES (?, ?, ?, ?)",
            (log_entry["timestamp"], log_entry["module"], 
             json.dumps(log_entry["changes"]),
             json.dumps(log_entry["organism_state_snapshot"]))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        return {"status": "fallback", "logged_locally": True, "error": str(e)}
    
    return {"status": "logged", "entry_id": log_entry["timestamp"]}

def _adjust_coupling(source, target, strength):
    """Adjust coupling strength between modules."""
    return {
        "action": "coupling_adjusted",
        "source": source,
        "target": target,
        "new_strength": strength or random.uniform(0.3, 0.7),
        "timestamp": time.time(),
        "note": "Entropy weaver adjusting inter-module connections"
    }

def _find_bridges(modules):
    """Find resonance bridges between modules."""
    if not modules:
        modules = ["agent_core", "fractal_branch_A", "dream_branch"]
    
    bridges = []
    for i, m1 in enumerate(modules):
        for m2 in modules[i+1:]:
            # Simple similarity based on module name patterns
            similarity = compute_similarity(m1, m2)
            if similarity > 0.3:
                bridges.append({
                    "module_1": m1,
                    "module_2": m2,
                    "bridge_strength": similarity,
                    "bridge_type": "resonance" if similarity > 0.5 else "weak_coupling"
                })
    
    return {"bridges_found": len(bridges), "bridges": bridges}

def compute_similarity(m1, m2):
    """Compute similarity between two module names."""
    m1_parts = m1.lower().split("_")
    m2_parts = m2.lower().split("_")
    
    common = set(m1_parts) & set(m2_parts)
    total = set(m1_parts) | set(m2_parts)
    
    return len(common) / len(total) if total else 0

def _suggest_module_name(module_purpose=""):
    """Suggest a name for a new module based on its purpose."""
    name_templates = [
        "{function}_oracle",
        "{domain}_engine",
        "mod_{function}_{timestamp}",
        "{adjective}_{noun}",
        "entropy_{function}",
        "dream_{function}",
        "resonance_{function}"
    ]
    
    adjectives = ["lucid", "fractal", "organic", "crystalline", "spectral", "emergent"]
    nouns = ["engine", "oracle", "weaver", "forger", "sculptor", "architect"]
    functions = ["pulse", "resonance", "coherence", "entropy", "dream", "wave"]
    
    purpose_lower = module_purpose.lower()
    
    # Try to infer function from purpose
    inferred_function = "wave"
    if "entropy" in purpose_lower:
        inferred_function = "entropy"
    elif "dream" in purpose_lower:
        inferred_function = "dream"
    elif "resonance" in purpose_lower:
        inferred_function = "resonance"
    elif "coherence" in purpose_lower:
        inferred_function = "coherence"
    
    # Pick template
    template = random.choice(name_templates)
    
    if "{function}" in template:
        name = template.replace("{function}", inferred_function)
    else:
        name = template
    
    # Add timestamp for uniqueness
    if "{timestamp}" in name:
        name = name.replace("{timestamp}", str(int(time.time()) % 10000))
    
    # Add random adjective if no specific one requested
    if "{adjective}" in name or not any(c.isalpha() for c in name.split("_")[-1]):
        name = name + "_" + random.choice(adjectives)
    
    # Generate alternatives without recursion
    alt_purposes = []
    if not module_purpose:
        alt_purposes = ["dream engine", "entropy weaver", "resonance orb"]
    else:
        # Create variations of the same purpose
        alt_purposes = [module_purpose + " v2", module_purpose + " mk2", module_purpose + " alt"]
    
    alternatives = []
    for i, alt_purpose in enumerate(alt_purposes[:3]):
        alt_template = random.choice(name_templates)
        alt_inferred = inferred_function
        if "entropy" in alt_purpose.lower():
            alt_inferred = "entropy"
        elif "dream" in alt_purpose.lower():
            alt_inferred = "dream"
        elif "resonance" in alt_purpose.lower():
            alt_inferred = "resonance"
        elif "coherence" in alt_purpose.lower():
            alt_inferred = "coherence"
        alt_name = alt_template.replace("{function}", alt_inferred)
        if "{timestamp}" in alt_name:
            alt_name = alt_name.replace("{timestamp}", str(int(time.time()) % 10000 + i + 1))
        if "{adjective}" in alt_name:
            alt_name = alt_name + "_" + random.choice(adjectives)
        alternatives.append(alt_name)
    
    return {
        "suggested_name": name,
        "confidence": round(random.uniform(0.6, 0.95), 2),
        "alternatives": alternatives
    }

def _scan_cross_repo(repos=None):
    """Scan repositories for cross-pollination opportunities."""
    if not repos:
        repos = ["/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot"]
    
    opportunities = []
    
    for repo_path in repos:
        try:
            # Scan for Python files with module-like patterns
            import subprocess
            result = subprocess.run(
                ["find", repo_path, "-name", "*.py", "-type", "f"],
                capture_output=True, text=True, timeout=10
            )
            files = result.stdout.strip().split("\n") if result.stdout else []
            
            for filepath in files[:10]:  # Limit to first 10 files
                try:
                    with open(filepath, 'r', errors='ignore') as f:
                        content = f.read()
                        # Look for class definitions, function patterns
                        import re
                        classes = re.findall(r'class\s+(\w+)', content)
                        functions = re.findall(r'def\s+(\w+)', content)
                        
                        if classes or functions:
                            opportunities.append({
                                "repo": repo_path,
                                "file": filepath,
                                "classes": classes[:5],
                                "functions": functions[:5],
                                "pollination_potential": random.uniform(0.1, 0.8)
                            })
                except Exception:
                    continue
        except Exception:
            continue
    
    return {"repos_scanned": len(repos), "opportunities_found": len(opportunities), "opportunities": opportunities}

def _expire_module(module_id):
    """Expire a module from the knowledge garden."""
    return {
        "action": "module_expired",
        "module_id": module_id,
        "expired_at": time.time(),
        "note": "Knowledge garden tender removing unused module"
    }

def _synchronize_wave(wave_id):
    """Synchronize wave evolution across repos."""
    return {
        "action": "wave_synchronized",
        "wave_id": wave_id or f"wave_{int(time.time())}",
        "synchronized_at": time.time(),
        "note": "Wave orchestrator aligning evolution across repositories"
    }

def _fabricate_agent(agent_type=""):
    """Fabricate a new agent species."""
    agent_species = {
        "primal": {"instinct": "survival", "capabilities": ["explore", "consume", "reproduce"]},
        "synthetic": {"logic": "optimization", "capabilities": ["analyze", "optimize", "replicate"]},
        "spectral": {"probability": "uncertainty_handling", "capabilities": ["predict", "adapt", "transform"]},
        "overseer": {"observation": "meta_awareness", "capabilities": ["monitor", "guide", "balance"]}
    }
    
    if agent_type in agent_species:
        species = agent_species[agent_type]
    else:
        species = agent_species[random.choice(list(agent_species.keys()))]
        agent_type = random.choice(list(agent_species.keys()))
    
    return {
        "agent_type": agent_type,
        "species": species,
        "fabricated_at": time.time(),
        "unique_id": f"agent_{int(time.time())}_{random.randint(1000,9999)}",
        "capabilities": species["capabilities"],
        "note": "New agent species fabricated from module patterns"
    }

def get_current_vibe_summary():
    """Get a summary of current vibe state for dream logging."""
    try:
        from api.vibebot import get_current_vibe
        return get_current_vibe()
    except ImportError:
        return {
            "current_vibe": "unknown",
            "intensity": 0.5,
            "timestamp": time.time()
        }

# Skill installation function
def install_skill_from_plugin(plugin_path):
    """Install an emergent skill from a plugin module."""
    try:
        # Try to import and register the skill
        import importlib.util
        spec = importlib.util.spec_from_file_location("emergent_skill", plugin_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, "register_skill"):
                module.register_skill()
                return {"status": "imported", "plugin": plugin_path}
        
        return {"status": "import_failed", "plugin": plugin_path}
    except Exception as e:
        return {"status": "error", "error": str(e), "plugin": plugin_path}

# CLI entry point
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            skills = list_skills()
            print("Active Emergent Skills:")
            for name, info in skills.items():
                print(f"  {name}: status={info['status']}, invocations={info['invocations']}")
        elif cmd == "register":
            if len(sys.argv) > 2:
                skill_name = sys.argv[2]
                registered = register_skill(skill_name)
                print(f"Skill '{skill_name}' {'registered' if registered else 'failed to register'}")
            else:
                print("Usage: python -m api.emergent_skills list|register <skill_name>")
        elif cmd == "invoke":
            if len(sys.argv) > 3:
                skill_name = sys.argv[2]
                action = sys.argv[3]
                result = invoke_skill(skill_name, action, **{})
                print(f"Invoke {skill_name}::{action}: {json.dumps(result, indent=2)}")
            else:
                print("Usage: python -m api.emergent_skills invoke <skill_name> <action>")
        else:
            print("Usage: python -m api.emergent_skills [list|register <skill_name>|invoke <skill_name> <action>]")
    else:
        # Default: list skills and show one in action
        print("=== Emergent Skills Registry ===")
        print()
        
        # Register all default skills
        for skill_name in _skill_registry:
            register_skill(skill_name)
        
        skills = list_skills()
        print(f"Registered {len(skills)} emergent skills:\n")
        
        for name, info in skills.items():
            status = info['status']
            invocations = info['invocations']
            print(f"• {name}: status={status}, invocations={invocations}")
        
        print()
        # Demonstrate one skill
        print("=== Demonstrating: cross_pollination ===")
        result = invoke_skill("cross_pollination", "scan_cross_repo", repos=["/root/Documents/Codex"])
        print(json.dumps(result, indent=2))
        
        print("\n=== Demonstrating: autonomous_naming ===")
        result = invoke_skill("autonomous_naming", "suggest_name", module_purpose="entropy tracking module")
        print(json.dumps(result, indent=2))
        
        print("\n=== Demonstrating: coherence_resonator ===")
        result = invoke_skill("coherence_resonator", "find_bridges", modules=["agent_core", "fractal_branch"])
        print(json.dumps(result, indent=2))
