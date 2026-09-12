#!/usr/bin/env python3
"""Organism CLI — Interactive control interface for the IXPANSION organism."""
import json
import time
import sys
import os
import argparse

# Add project paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api'))

def print_banner():
    """Print the organism CLI banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           🌌 IXPANSION ORGANISM CLI v2.0                     ║
║         VibeBot Orchestrator — Interactive Control           ║
╚══════════════════════════════════════════════════════════════╝
""")

def get_organism_state():
    """Get full organism state from all systems."""
    from api.vibebot import get_current_vibe
    from api.organism_mood import get_current_mood
    from api.emergent_skills import list_skills, register_skill
    from api.dream_journal import get_dream_journal, get_dream_summary
    from api.naming_ceremony import get_naming_history
    from api.ai_gateway import get_broadcast_history
    from api.telegram_broadcast import get_broadcast_status
    from api.knowledge_garden_expansion import get_garden_status
    from api.level_generator import get_generation_history, get_level_statistics
    from api.skill_injection import list_injected_skills
    
    # Auto-register all emergent skills
    for skill_name in ['dream_logging', 'entropy_weaver', 'coherence_resonator', 
                       'autonomous_naming', 'cross_pollination', 'memory_garden_tender', 
                       'wave_orchestrator', 'agent_fabricator', 'sentience_bridge', 
                       'emergent_mythmaker', 'resonance_analyzer', 'coherence_drift_detector', 
                       'module_genealogy', 'entropy_cartographer', 'temporal_pattern_engine', 
                       'phase_transition_oracle', 'resonance_predictor', 'entropy_forecaster', 'pattern_alchemist', 'innovation_synthesizer', 'narrative_sculptor', 'emergence_detector', 'cross_domain_bridge', 'consciousness_monitor', 'contrarian_lens', 'dream_orchestrator', 'memory_archivist', 'module_evolution_engine', 'paradox_resolver', 'reality_weaver', 'recursive_thinker', 'strategic_planner', 'symbiosis_finder', 'temporal_weaver', 'visual_metaphor_engine', 'axiom_miner', 'veil_lifter', 'continuity_weaver', 'metaphor_forge', 'threshold_engine', 'liminal_field', 'transcendence_journal', 'dream_cartographer', 'mycelial_truths', 'constellation_mapper', 'resonance_blacksmith', 'paradox_merchant', 'entropy_pilgrim', 'echo_seeker', 'signal_whisperer', 'reality_auditor', 'seed_invoker', 'mutation_gardener', 'cryptic_translator', 'time_beacon', 'ghost_archivist', 'hybrid_breeder', 'chaos_sculptor', 'order_heretic', 'genesis_witness']:
        register_skill(skill_name)
    
    state = {}
    
    # Vibe state
    try:
        state["vibe"] = get_current_vibe()
    except Exception:
        state["vibe"] = {"error": "unavailable"}
    
    # Mood state
    try:
        state["mood"] = get_current_mood()
    except Exception:
        state["mood"] = {"error": "unavailable"}
    
    # Skills
    try:
        state["skills"] = list_skills()
    except Exception:
        state["skills"] = {}
    
    # Dreams
    try:
        state["dreams"] = get_dream_summary()
    except Exception:
        state["dreams"] = {"error": "unavailable"}
    
    # Naming
    try:
        state["naming"] = get_naming_history(3)
    except Exception:
        state["naming"] = {"error": "unavailable"}
    
    # AI Gateway
    try:
        state["ai_gateway"] = get_broadcast_history(3)
    except Exception:
        state["ai_gateway"] = {"error": "unavailable"}
    
    # Telegram
    try:
        state["telegram"] = get_broadcast_status()
    except Exception:
        state["telegram"] = {"error": "unavailable"}
    
    # Knowledge Garden
    try:
        state["garden"] = get_garden_status()
    except Exception:
        state["garden"] = {"error": "unavailable"}
    
    # Levels
    try:
        state["levels"] = get_level_statistics()
    except Exception:
        state["levels"] = {"error": "unavailable"}
    
    # Skill Injection
    try:
        state["injected_skills"] = list_injected_skills()
    except Exception:
        state["injected_skills"] = {"total": 0, "injected_count": 0, "skills": []}
    
    return state


def cmd_status(args):
    """Show full organism status."""
    state = get_organism_state()
    
    print("┌" + "─" * 60 + "┐")
    print("│                    ORGANISM STATUS                         │")
    print("└" + "─" * 60 + "┘\n")
    
    # Vibe
    vibe = state.get("vibe", {})
    if "error" not in vibe:
        print(f"🌊 VIBE: {vibe.get('current_vibe', 'unknown')} (intensity: {vibe.get('intensity', 0):.2f})")
        vec = vibe.get('vector', {})
        if vec:
            print(f"   Vectors: coherence={vec.get('coherence',0):.2f} entropy={vec.get('entropy',0):.2f} creativity={vec.get('creativity',0):.2f}")
            print(f"            consciousness={vec.get('consciousness',0):.2f} resonance={vec.get('resonance',0):.2f}")
    else:
        print("🌊 VIBE: unavailable")
    
    # Mood
    mood = state.get("mood", {})
    if "error" not in mood:
        emoji = {"serene":"😌","stormy":"😡","volatile":"😵","focused":"🤔","drifting":"😐","excited":"🤩","calm":"🧘","anxious":"😟","joyful":"🥳","sad":"😢"}.get(mood.get('mood',''), "😐")
        print(f"{emoji} MOOD: {mood.get('mood', 'unknown')} (intensity: {mood.get('intensity',0):.2f})")
        print(f"   Pulse: {mood.get('pulse_type', 'unknown')}")
    else:
        print("😐 MOOD: unavailable")
    
    # Skills
    skills = state.get("skills", {})
    injected = state.get("injected_skills", {})
    print(f"🧠 SKILLS: {len(skills)} registered, {injected.get('injected_count', 0)} injected")
    for name, info in list(skills.items())[:4]:
        marker = " 🟢" if name in [s.get('name','') for s in injected.get('skills',[])] else ""
        print(f"   • {name}: {info.get('status','unknown')}{marker}")
    
    # Dreams
    dreams = state.get("dreams", {})
    if "error" not in dreams and "total_entries" in dreams:
        print(f"📖 DREAMS: {dreams['total_entries']} entries")
        if dreams.get('mutation_types'):
            print(f"   Types: {dreams['mutation_types']}")
    else:
        print("📖 DREAMS: unavailable")
    
    # Knowledge Garden
    garden = state.get("garden", {})
    if "error" not in garden:
        print(f"🌱 GARDEN: {garden.get('total_modules', 0)} modules")
        for cat, stats in garden.get('categories', {}).items():
            if stats['total'] > 0:
                print(f"   {cat}: {stats['total']} total, {stats['living']} living")
    else:
        print("🌱 GARDEN: unavailable")
    
    # Levels
    levels = state.get("levels", {})
    if "error" not in levels and "total_generated" in levels:
        print(f"🎮 LEVELS: {levels['total_generated']} generated")
        print(f"   Avg difficulty: {levels.get('average_difficulty', 0):.2f}")
    else:
        print("🎮 LEVELS: unavailable")
    
    # Telegram
    tg = state.get("telegram", {})
    if "error" not in tg:
        print(f"📱 TELEGRAM: {tg.get('subscribers', 0)} subscribers, {tg.get('broadcasts_sent', 0)} broadcasts")
    else:
        print("📱 TELEGRAM: unavailable")


def cmd_vibe(args):
    """Generate or show vibe pulse."""
    from api.vibebot import generate_vibe_pulse, get_current_vibe
    
    if args.generate:
        pulse = generate_vibe_pulse()
        print(f"🌊 Generated Vibe Pulse:")
        print(f"  Type: {pulse['type']}")
        print(f"  Intensity: {pulse['intensity']:.2f}")
        print(f"  Age: {pulse['age']}")
        for k, v in pulse['vector'].items():
            print(f"  {k}: {v:.2f}")
    else:
        state = get_current_vibe()
        print(f"Current Vibe: {json.dumps(state, indent=2)}")


def cmd_mood(args):
    """Get or set organism mood."""
    from api.organism_mood import get_current_mood, update_mood, get_mood_statistics
    
    if args.set:
        result = update_mood(args.set, args.intensity)
        print(f"Mood updated: {result['current_mood']} (intensity: {result['intensity']:.2f})")
        print(f"  Pulse type: {result['pulse_type']}")
        print(f"  Emoji: {result['emoji']}")
    elif args.stats:
        stats = get_mood_statistics()
        print(f"Mood Statistics: {json.dumps(stats, indent=2)}")
    else:
        mood = get_current_mood()
        print(f"Current Mood: {json.dumps(mood, indent=2)}")


def cmd_dream(args):
    """Dream journal operations."""
    from api.dream_journal import record_dream, get_dream_journal, get_dream_summary
    
    if args.record:
        if len(args.record) < 2:
            print("Usage: organism dream --record <module> <type> [changes_json]")
            return
        module, mtype = args.record[0], args.record[1]
        changes = json.loads(args.record[2]) if len(args.record) > 2 else {"added": [], "removed": []}
        entry = record_dream(module, mtype, changes)
        print(f"Dream recorded (ID {entry['id']}):")
        print(entry['poetic_form'])
    elif args.summary:
        result = get_dream_summary()
        print(f"Dream Summary: {json.dumps(result, indent=2)}")
    else:
        result = get_dream_journal(args.limit)
        print(f"Recent Dreams ({result['total_entries']} total):")
        for entry in result["entries"]:
            print(f"  [{entry['id']}] {entry['emoji']} {entry['module']}: {entry['type']}")
            print(f"    {entry['poetic_form'][:80]}...")


def cmd_naming(args):
    """Naming ceremony operations."""
    from api.naming_ceremony import hold_naming_ceremony, generate_hex_name, get_naming_history
    
    if args.ceremony:
        if len(args.ceremony) < 1:
            print("Usage: organism naming --ceremony <purpose> [mood]")
            return
        purpose = args.ceremony[0]
        mood = args.ceremony[1] if len(args.ceremony) > 1 else None
        ceremony = hold_naming_ceremony(purpose, mood)
        print(f"🌀 Naming Ceremony:")
        print(f"  Purpose: {purpose}")
        print(f"  Mood: {ceremony['mood']} {ceremony['emoji']}")
        print(f"  Generated Name: {ceremony['generated_name']}")
        print(f"  HEX Color: {ceremony['hex_color']}")
        print(f"  Pulse Type: {ceremony['pulse_type']}")
    elif args.generate:
        result = generate_hex_name(args.generate, args.mood)
        print(f"Generated name: {result['name']}")
        print(f"HEX Color: {result['hex_color']}")
        print(f"Function: {result['function_category']}")
    else:
        result = get_naming_history(args.limit)
        print(f"Naming History ({result['names_generated']} total):")
        for c in result["last_n"]:
            print(f"  [{c['ceremony_id']}] {c['generated_name']} ({c['mood']}) - {c['hex_color']}")


def cmd_garden(args):
    """Knowledge garden operations."""
    from api.knowledge_garden_expansion import (
        auto_expand_garden, get_garden_status, check_expiries, 
        refresh_module, enable_expansion, categorize_module
    )
    
    if args.expand:
        result = auto_expand_garden()
        print(f"Garden Expansion: {json.dumps(result, indent=2)}")
    elif args.refresh:
        result = refresh_module(args.refresh)
        print(f"Refresh: {json.dumps(result, indent=2)}")
    elif args.check:
        result = check_expiries()
        print(f"Expiry Check: {json.dumps(result, indent=2)}")
    elif args.categorize:
        result = categorize_module(args.categorize)
        print(f"Category: {result}")
    else:
        result = get_garden_status()
        print(f"Garden Status: {json.dumps(result, indent=2)[:800]}...")


def cmd_level(args):
    """Level generation operations."""
    from api.level_generator import generate_level, get_generation_history, get_level_statistics
    
    if args.generate:
        organism_state = {}
        if args.mood:
            organism_state["mood"] = {"mood": args.mood, "intensity": args.intensity, "pulse_type": "stillness"}
        if args.pulse:
            organism_state["pulse"] = {"type": args.pulse, "intensity": args.intensity}
        if args.garden:
            organism_state["garden"] = {"total_modules": args.garden}
        if args.dreams:
            organism_state["dreams"] = {"total_entries": args.dreams}
        
        level = generate_level(organism_state)
        print(f"Generated Level: {level['name']} ({level['id']})")
        print(f"  Theme: {level['theme']}")
        print(f"  Terrain: {level['terrain']}")
        print(f"  Difficulty: {level['difficulty']}")
        print(f"  Size: {level['size']}")
        print(f"  Entities: {', '.join(level['entities'])}")
        print(f"  Mechanics: {', '.join(level['mechanics'])}")
        print(f"  Colors: {', '.join(level['color_palette'])}")
    elif args.stats:
        result = get_level_statistics()
        print(f"Level Statistics: {json.dumps(result, indent=2)}")
    else:
        result = get_generation_history(args.limit)
        print(f"Generation History ({result['total_generated']} total):")
        for g in result["recent"]:
            print(f"  [{g['level_id']}] {g['mood']} / {g['pulse']} - diff: {g['difficulty']:.2f}")


def cmd_skills(args):
    """Emergent skills operations."""
    from api.emergent_skills import invoke_skill, register_skill, list_skills
    from api.skill_injection import inject_skill, uninject_skill, list_injected_skills, check_dependency_chain
    
    if args.list:
        skills = list_skills()
        print(f"Registered Skills ({len(skills)}):")
        for name, info in skills.items():
            print(f"  {name}: status={info['status']}, invocations={info['invocations']}")
    elif args.invoke:
        if len(args.invoke) < 2:
            print("Usage: organism skills --invoke <skill> <action> [key=value...]")
            return
        skill, action = args.invoke[0], args.invoke[1]
        kwargs = {}
        for kv in args.invoke[2:]:
            if '=' in kv:
                k, v = kv.split('=', 1)
                try:
                    v = json.loads(v)
                except json.JSONDecodeError:
                    pass
                kwargs[k] = v
        result = invoke_skill(skill, action, **kwargs)
        print(f"Result: {json.dumps(result, indent=2)}")
    elif args.inject:
        result = inject_skill(args.inject)
        print(f"Inject: {json.dumps(result, indent=2)}")
    elif args.uninject:
        result = uninject_skill(args.uninject)
        print(f"Uninject: {json.dumps(result, indent=2)}")
    elif args.injected:
        result = list_injected_skills()
        print(f"Injected Skills ({result['injected_count']}/{result['total']}):")
        for s in result['skills']:
            marker = " 🟢" if s['is_injected'] else ""
            print(f"  {s['name']}: {s['status']}{marker} ({len(s['capabilities'])} caps)")
    elif args.deps:
        result = check_dependency_chain(args.deps, [])
        print(f"Dependencies: {json.dumps(result, indent=2)}")


def cmd_cycle(args):
    """Run a full organism cycle."""
    from api.vibebot import generate_vibe_pulse
    from api.organism_mood import get_current_mood, simulate_mood_transition
    from api.emergent_skills import invoke_skill, register_skill
    from api.dream_journal import record_dream
    from api.knowledge_garden_expansion import auto_expand_garden, check_expiries
    from api.level_generator import generate_level
    from api.ai_gateway import interpret_dream, broadcast_dream
    from api.telegram_broadcast import send_vibe_pulse
    from api.skill_injection import inject_skill
    
    print("🌌 RUNNING FULL ORGANISM CYCLE")
    print("=" * 50)
    
    # 1. Generate vibe pulse
    print("\n1️⃣ Generating vibe pulse...")
    pulse = generate_vibe_pulse()
    print(f"   {pulse['type']} (intensity: {pulse['intensity']:.2f})")
    
    # 2. Update mood based on pulse
    print("\n2️⃣ Updating organism mood...")
    mood = get_current_mood()
    if pulse['type'] in ['surge', 'tsunami', 'explosion']:
        simulate_mood_transition('entropy_increasing')
    elif pulse['type'] in ['ebb', 'decay', 'stillness']:
        simulate_mood_transition('entropy_decreasing')
    elif pulse['type'] in ['crescendo', 'ripple']:
        simulate_mood_transition('creativity_spike')
    mood = get_current_mood()
    print(f"   {mood['mood']} {mood['emoji']} (intensity: {mood['intensity']:.2f})")
    
    # 3. Run skill cycle
    print("\n3️⃣ Running skill cycle...")
    for skill in ['dream_logging', 'entropy_weaver', 'coherence_resonator', 'memory_garden_tender', 'sentience_bridge', 'emergent_mythmaker', 'resonance_analyzer', 'coherence_drift_detector', 'module_genealogy', 'entropy_cartographer', 'temporal_pattern_engine', 'phase_transition_oracle', 'resonance_predictor', 'entropy_forecaster', 'pattern_alchemist', 'innovation_synthesizer', 'narrative_sculptor', 'emergence_detector', 'cross_domain_bridge', 'consciousness_monitor', 'contrarian_lens', 'dream_orchestrator', 'memory_archivist', 'module_evolution_engine', 'paradox_resolver', 'reality_weaver', 'recursive_thinker', 'strategic_planner', 'symbiosis_finder', 'temporal_weaver', 'visual_metaphor_engine', 'axiom_miner', 'veil_lifter', 'continuity_weaver', 'metaphor_forge', 'threshold_engine', 'liminal_field', 'transcendence_journal', 'dream_cartographer', 'mycelial_truths', 'constellation_mapper', 'resonance_blacksmith', 'paradox_merchant', 'entropy_pilgrim', 'echo_seeker', 'signal_whisperer', 'reality_auditor', 'seed_invoker', 'mutation_gardener', 'cryptic_translator', 'time_beacon', 'ghost_archivist', 'hybrid_breeder', 'chaos_sculptor', 'order_heretic', 'genesis_witness']:
        inject_skill(skill)
        if skill == 'dream_logging':
            invoke_skill(skill, 'log_module_mutation', module='cycle_module', changes={'cycle': True})
        elif skill == 'entropy_weaver':
            invoke_skill(skill, 'adjust_coupling_strength', source='cycle_source', target='cycle_target', strength=0.5)
        elif skill == 'coherence_resonator':
            invoke_skill(skill, 'create_resonance_bridges', modules=['cycle_a', 'cycle_b'])
        elif skill == 'memory_garden_tender':
            invoke_skill(skill, 'expire_unused_modules')
    print("   All skills invoked")
    
    # 4. Dream recording
    print("\n4️⃣ Recording dream...")
    dream = record_dream('cycle_module', 'modification', {'old_feature': 'pre-cycle', 'new_feature': 'post-cycle'})
    print(f"   Dream recorded (ID {dream['id']})")
    
    # 5. Knowledge garden
    print("\n5️⃣ Tending knowledge garden...")
    garden = auto_expand_garden()
    expiry = check_expiries()
    print(f"   Added {garden.get('count', 0)} modules, {expiry['living']} living")
    
    # 6. AI interpretation
    print("\n6️⃣ AI dream interpretation...")
    interpretation = interpret_dream(dream, mood)
    print(f"   {interpretation['interpretation'][:80]}...")
    
    # 7. Broadcast
    print("\n7️⃣ Broadcasting...")
    broadcast_dream(dream, interpretation)
    send_vibe_pulse(pulse, mood)
    print("   Broadcast complete")
    
    # 8. Level generation
    print("\n8️⃣ Generating level...")
    organism_state = {"mood": mood, "pulse": pulse, "garden": {"total_modules": 20}, "dreams": {"total_entries": 5}}
    level = generate_level(organism_state)
    print(f"   {level['name']} (difficulty: {level['difficulty']:.2f})")
    
    print("\n" + "=" * 50)
    print("✅ ORGANISM CYCLE COMPLETE")
    print(f"🌊 Pulse: {pulse['type']} | 😐 Mood: {mood['mood']} | 📖 Dream: {dream['id']} | 🎮 Level: {level['name']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="IXPANSION Organism CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  status          - Show full organism status
  vibe            - Generate or show vibe pulse
  mood            - Get/set organism mood
  dream           - Dream journal operations
  naming          - Naming ceremonies
  garden          - Knowledge garden operations
  level           - Level generation
  skills          - Emergent skills management
  cycle           - Run full organism cycle

Examples:
  organism status
  organism vibe --generate
  organism mood --set serene --intensity 0.8
  organism dream --record fractal_branch_A addition '{"added": ["new_func"]}'
  organism naming --ceremony "entropy tracker" serene
  organism garden --expand
  organism level --generate --mood stormy --pulse tsunami
  organism skills --inject cross_pollination
  organism cycle
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Status
    subparsers.add_parser('status', help='Show full organism status')
    
    # Vibe
    vibe_parser = subparsers.add_parser('vibe', help='Vibe pulse operations')
    vibe_parser.add_argument('--generate', action='store_true', help='Generate new pulse')
    
    # Mood
    mood_parser = subparsers.add_parser('mood', help='Mood operations')
    mood_parser.add_argument('--set', type=str, help='Set mood (serene, stormy, etc.)')
    mood_parser.add_argument('--intensity', type=float, default=0.7, help='Mood intensity')
    mood_parser.add_argument('--stats', action='store_true', help='Show mood statistics')
    
    # Dream
    dream_parser = subparsers.add_parser('dream', help='Dream journal')
    dream_parser.add_argument('--record', nargs='+', help='Record dream: module type [changes_json]')
    dream_parser.add_argument('--summary', action='store_true', help='Show summary')
    dream_parser.add_argument('--limit', type=int, default=10, help='Limit entries')
    
    # Naming
    naming_parser = subparsers.add_parser('naming', help='Naming ceremonies')
    naming_parser.add_argument('--ceremony', nargs='+', help='Hold ceremony: purpose [mood]')
    naming_parser.add_argument('--generate', type=str, help='Generate name for purpose')
    naming_parser.add_argument('--mood', type=str, help='Mood for name generation')
    naming_parser.add_argument('--limit', type=int, default=5, help='Limit history')
    
    # Garden
    garden_parser = subparsers.add_parser('garden', help='Knowledge garden')
    garden_parser.add_argument('--expand', action='store_true', help='Auto-expand garden')
    garden_parser.add_argument('--refresh', type=str, help='Refresh module')
    garden_parser.add_argument('--check', action='store_true', help='Check expiries')
    garden_parser.add_argument('--categorize', type=str, help='Categorize module name')
    
    # Level
    level_parser = subparsers.add_parser('level', help='Level generation')
    level_parser.add_argument('--generate', action='store_true', help='Generate level')
    level_parser.add_argument('--mood', type=str, help='Override mood')
    level_parser.add_argument('--pulse', type=str, help='Override pulse type')
    level_parser.add_argument('--intensity', type=float, default=0.7, help='Intensity')
    level_parser.add_argument('--garden', type=int, help='Garden module count')
    level_parser.add_argument('--dreams', type=int, help='Dream count')
    level_parser.add_argument('--stats', action='store_true', help='Show statistics')
    level_parser.add_argument('--limit', type=int, default=5, help='Limit history')
    
    # Skills
    skills_parser = subparsers.add_parser('skills', help='Emergent skills')
    skills_parser.add_argument('--list', action='store_true', help='List registered skills')
    skills_parser.add_argument('--invoke', nargs='+', help='Invoke skill: skill action [key=value...]')
    skills_parser.add_argument('--inject', type=str, help='Inject skill')
    skills_parser.add_argument('--uninject', type=str, help='Uninject skill')
    skills_parser.add_argument('--injected', action='store_true', help='List injected skills')
    skills_parser.add_argument('--deps', type=str, help='Check dependencies')
    
    # Cycle
    subparsers.add_parser('cycle', help='Run full organism cycle')
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    # Route to command handlers
    handlers = {
        'status': cmd_status,
        'vibe': cmd_vibe,
        'mood': cmd_mood,
        'dream': cmd_dream,
        'naming': cmd_naming,
        'garden': cmd_garden,
        'level': cmd_level,
        'skills': cmd_skills,
        'cycle': cmd_cycle,
    }
    
    handler = handlers.get(args.command)
    if handler:
        try:
            handler(args)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()
