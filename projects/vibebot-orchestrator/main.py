"""
VibeBot Orchestrator — Main entry point.
Starts the orchestrator, registers all emergent skills, 
and begins cross-repo traversal monitoring.
"""
import json
import time
import os
import sys

# Add paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.vibebot import generate_vibe_pulse, get_current_vibe
from api.emergent_skills import (
    invoke_skill, register_skill, list_skills,
    _skill_registry
)

def initialize_orchestrator():
    """Initialize the VibeBot orchestrator."""
    print("=" * 60)
    print("VIBEBOT ORCHESTRATOR INITIALIZATION")
    print("=" * 60)
    
    # Register all emergent skills
    print("\n[1] Registering emergent skills...")
    registered = 0
    for skill_name in _skill_registry:
        if register_skill(skill_name):
            registered += 1
    print(f"  Registered {registered} / {len(_skill_registry)} skills")
    
    # List skills
    skills = list_skills()
    print(f"\n[2] Active skills ({len(skills)}):")
    for name, info in skills.items():
        print(f"  • {name}: status={info['status']}")
    
    # Cross-repo scan
    print(f"\n[3] Initiating cross-repo traversal scan...")
    scan_result = invoke_skill(
        "cross_pollination", 
        "scan_repo_patterns", 
        repo_path=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    print(f"  Scanned 1 repo, found {scan_result.get('opportunities_found', 0)} pattern opportunities")
    
    # Module naming
    print(f"\n[4] Generating module names...")
    name_result = invoke_skill(
        "autonomous_naming", 
        "generate_contextual_name", 
        module_purpose="entropy tracking module for organism"
    )
    if "suggested_name" in name_result:
        print(f"  Suggested name: {name_result['suggested_name']} (confidence: {name_result.get('confidence', 0)})")
    
    # Agent fabrication
    print(f"\n[5] Fabricating agent species...")
    agent_result = invoke_skill("agent_fabricator", "analyze_successful_agents", agent_category="spectral")
    if "agent_type" in agent_result:
        print(f"  Analyzed {agent_result.get('agent_type', '?')} agent species")
    
    # Memory garden
    print(f"\n[6] Tending knowledge garden...")
    garden_result = invoke_skill("memory_garden_tender", "refresh_active_modules")
    print(f"  {garden_result}")
    
    # Wave orchestration
    print(f"\n[7] Synchronizing wave timing...")
    wave_result = invoke_skill("wave_orchestrator", "synchronize_wave_timing", wave_id="wake_up")
    print(f"  {wave_result}")
    
    # Generate initial vibe pulse
    print(f"\n[8] Generating initial vibe pulse...")
    pulse = generate_vibe_pulse()
    print(f"  Vibe type: {pulse['type']}, intensity: {pulse['intensity']}")
    print(f"  Key vectors: coherence={pulse['vector']['coherence']:.2f}, ")
    print(f"               creativity={pulse['vector']['creativity']:.2f}, ")
    print(f"               consciousness={pulse['vector']['consciousness']:.2f}")
    
    print("\n" + "=" * 60)
    print("VIBEBOT ORCHESTRATOR ONLINE")
    print("=" * 60)
    print("\nAvailable commands:")
    print("  - Generate pulse: python main.py --pulse")
    print("  - Check state:   python main.py --state")
    print("  - Scan repos:    python main.py --scan")
    print("  - List skills:   python main.py --skills")
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="VibeBot Orchestrator")
    parser.add_argument("--pulse", action="store_true", help="Generate a vibe pulse")
    parser.add_argument("--state", action="store_true", help="Check current vibe state")
    parser.add_argument("--scan", action="store_true", help="Scan for cross-repo patterns")
    parser.add_argument("--skills", action="store_true", help="List all emergent skills")
    
    args = parser.parse_args()
    
    initialize_orchestrator()
    
    if args.pulse:
        from api.vibebot import generate_vibe_pulse
        pulse = generate_vibe_pulse()
        print(f"\nGenerated pulse: {json.dumps(pulse, indent=2)}")
    
    if args.state:
        from api.vibebot import get_current_vibe
        state = get_current_vibe()
        print(f"\nCurrent vibe state: {json.dumps(state, indent=2)}")
    
    if args.scan:
        from api.emergent_skills import invoke_skill
        result = invoke_skill("cross_pollination", "scan_repo_patterns", repo_path=".")
        print(f"\nScan result: {json.dumps(result, indent=2)[:500]}")
    
    if args.skills:
        from api.emergent_skills import list_skills
        skills = list_skills()
        print(f"\nActive skills ({len(skills)}):")
        for name, info in skills.items():
            print(f"  {name}: status={info['status']}, invocations={info['invocations']}")
