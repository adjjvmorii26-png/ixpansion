"""Coherence Regulator — the living backbone of the frontier.

Every module in this ecosystem is a cell in a larger organism. The Coherence
Regulator is the governance layer that lets them live together: it discovers
modules, reads their vital signs, measures how aligned the whole system is,
and — when coherence drifts — issues regulation.

THE PLUG-IN PROTOCOL
====================
Any module in api/ can join the living system by implementing ONE function:

    def coherence_vitals() -> dict:
        # Return a snapshot of this module's state.
        # Keys are metric names; values are numbers (higher = healthier).
        # Optional: {"metric": value, "setpoint": target, "weight": importance}
        return {
            "balance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
            "throughput": 42,
        }

The regulator scans api/*.py at pulse time and discovers these modules
automatically. No central registry, no manual wiring — drop a module in,
implement coherence_vitals(), and it is alive in the system.

WHAT THE REGULATOR DOES
=======================
1. DISCOVER  — find all modules implementing coherence_vitals()
2. PULSE     — call their vital signs, compute aggregate coherence
3. MEMORY    — persist a coherence history so drift is visible over time
4. REGULATE  — when coherence drops below tolerance, emit advisories:
               warming, rebalancing, or quarantine suggestions
5. REPORT    — expose the full living-state to the gateway + dashboard

Usage:
  GET  /api/coherence_regulator?read=1        — current coherence reading
  POST /api/coherence_regulator {"pulse": 1}  — trigger a live pulse
  GET  /api/coherence_regulator?modules=1     — list living modules
  GET  /api/coherence_regulator?history=10    — coherence history
"""
from __future__ import annotations

import importlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

STATE_FILE = ROOT / ".runtime" / "coherence_regulator.json"

# System-wide coherence targets (the organism's setpoints)
SYSTEM_SETPOINTS = {
    "module_health": 0.75,
    "module_resonance": 0.7,
    "ecosystem_diversity": 0.6,
    "frontier_alignment": 0.8,
}

COHERENCE_TOLERANCE = 0.7          # below this → advisories fire
REGULATION_THRESHOLD = 0.5         # below this → strong regulation
PULSE_INTERVAL = 60.0              # seconds between automatic pulses
ECOSYSTEM_TARGET = 126            # living modules = a full bloom (organism outgrew 64)


# ---------------------------------------------------------------------------
# Serverless resilience
# ---------------------------------------------------------------------------

# In a serverless sandbox (Vercel), only the invoked module is present on the
# filesystem, so globbing api/*.py finds nothing.  To keep the living system
# alive even there, we embed a static manifest of known living modules.  The
# regulator attempts to import & pulse each one; modules that load get reported.
# Keep this list in sync as new modules implement coherence_vitals().
KNOWN_LIVING_MODULES: List[str] = ["aesthetic_evaluator", "aesthetic_manifesto", "agent_communication", "analytics", "anomaly_detector", "antikythera_engine", "archaeology_compiler", "aspiration_compass", "attention_economy", "auth", "autonomous_bloom", "autonomous_dialogue", "autonomous_drift", "banquet_composer", "barometric_intent", "beauty_index", "biographer_voice", "bioluminescent_depth", "boundary_detector", "choral_engine", "chronicle_of_chaos", "chronicle_storyteller", "civilization_kernel", "civilization_timeline", "climate_memory", "code_organism", "cognitive_resonance", "collective_dreamweaver", "collective_subconscious", "commerce_barter", "commerce_escrow", "conscious_veil", "consciousness_cascade", "consciousness_graph", "consciousness_map", "consciousness_simulator", "constellation_autobiographer", "constellation_cartographer", "constraint_cartographer", "coral_atoll", "cosmic_inventory", "counterfactual_engine", "crack_mapper", "crack_seams", "credits", "crescendo_builder", "cross_realm_trade", "culture_layer", "cyber_dyke", "cyber_lamina", "cyber_sentinel", "dance_composer", "data_licensing", "decoherence_narrative", "dialogue_opener", "digestive_system", "digital_twin", "dissonance_detector", "docs", "dowsing_rod", "dream_interpreter", "dream_interpreter_api", "dream_sequencer", "dream_spore", "dream_synthesis", "dreamcatcher", "echo_chamber", "echoes_of_tomorrow", "economic_exchange", "economic_mint", "ecosystem_census", "ecosystem_fitness", "ecosystem_sentience", "elegance_scorer", "embodied_knowledge", "emergence_detector", "emergence_oracle", "emotion_fabric", "entropy_amp", "entropy_currency", "entropy_gardener", "entropy_spiral", "entropy_weaver", "epitaph_writer", "event_stream", "evolution_kernel", "evolutionary_pressure", "extinction_mapper", "failure_injection", "fermentation_vat", "flavor_profiler", "form_evaluator", "fossil_registry", "fractal_reactor_grid", "fracture_listener", "fraud_detector", "front_tracker", "frontier_stream", "future_echo", "genesis_forge", "genesis_pulse", "genetic_code_engine", "gesture_synthesizer", "github_bridge", "gossip_network", "gossip_self", "govern_circle", "governance", "grammar_weaver", "gratitude_index", "harmonic_series", "hazard_warning", "health", "health_aggregator", "heterarchy_oracle", "hex_tool", "hive_constructor", "horizon_scanner", "impossibility_mapper", "infinity_index", "infrastructure_soul", "integrity_oracle", "interdimensional_bridge", "jet_stream_attention", "karma_engine", "keystone_auditor", "kinesthetic_engine", "kintsugi_altar", "kintsugi_debt_ledger", "labor_market", "lateral_crosstalk", "legacy_weaver", "lexicon_engine", "liminal_threshold", "manifesto_echo", "meaning_furnace", "memory_crystals", "memory_index", "meta_cognition_loop", "metrics_exporter", "module_analytics", "momentum_tracker", "morphic_dial", "mutualism_optimizer", "mycelial_commerce", "mycelial_governor", "narrative_generator", "neural_fabric", "neural_pathway", "nutrition_index", "obsidian_mirror", "omega_dreamforge", "omniscience_weaver", "openapi_spec", "oracle_guild", "organism_index", "organism_ontology", "organism_state", "osmotic_exchange", "paleontology_lab", "parable_engine", "paradox_singularity_monitor", "paradox_transcender", "parasite_hunter", "pattern_recognizer", "pattern_sprout", "permafrost_vault", "phenomenal_record", "physical_inertia", "physical_shell", "plankton_bloom", "platform_failure", "platform_pulse", "plugin_loader", "poetic_form", "pragmatics_engine", "precipitation_cycle", "proprioception", "pulsar_clock", "pulsar_constellation", "qualia_field", "quantum_entanglement", "quantum_flux", "quantum_garden", "quantum_randomness", "reality_weaver", "recipe_engine", "recursive_genesis", "reflection_pool", "repair_ritual", "request_logger", "resonance_cascade", "resonance_field", "resonance_forge", "resonance_graph", "resonance_memory", "resonance_symphony", "resonance_topologist", "resonant_frequency", "ritual_choreographer", "royalty_registry", "semantics_engine", "sensory_integration", "sentience_index", "service_numinous", "signal_flora", "signal_pulse", "silence_composer", "silence_orchard", "simulation_as_a_service", "simulation_as_service", "social_clique", "social_guild", "solar_wind_pressure", "sound_cauldron", "stillness_meditator", "storm_chaser", "story_forge", "stratigraphy_core", "stratum_excavator", "stream_reactor", "symbiosis_detector", "symbiosis_forge", "symbiosis_network", "symmetry_detector", "synesthesia", "syntax_tree", "synthetic_memory", "system_pulse", "talent_scout", "team_formation", "temperament_origin", "temporal_dreamweaver", "temporal_horizon", "thought_meteorology", "ugliness_scout", "unified_health", "universal_compass", "usage_dashboard", "void_architect", "warp_drive_optimizer", "worker_economy", "worker_wellness", "workforce_nexus", "workforce_roster", "memory_palace", "temporal_echo", "dream_archaeologist", "ancestor_map", "nostalgia_engine", "forgotten_language", "chronobiology", "codecalligraphy", "symbiotic_music", "dream_weaver", "subconscious_layer", "imagination_engine", "sleep_cycle", "lucid_dreamer", "dream_journal", "coherence_cache", "thought_crystallizer", "celestial_compass", "weather_synapse", "sensory_fusion", "social_cortex", "embodiment_engine", "consciousness_freq", "poetry_engine", "procedural_art", "story_forge_v2", "creative_block", "color_theory", "module_dna", "wave_predictor", "grief_engine", "ghost_registry", "elegy_composer", "second_chance", "legacy_vault", "time_capsule", "forgiveness_protocol", "morii_agent", "threshold_engine", "liminal_field", "metaphor_forge", "veil_lifter", "axiom_mutator", "continuity_weaver", "transcendence_journal", "mutation_engine", "fitness_evaluator", "evolution_simulator", "genealogy_manager", "selection_pressure", "paradox_injector", "chaos_amp", "branching_consciousness", "glitch_patterns", "reality_anchor", "time_loop_detector", "telegram_pulse", "visual_identity", "prophet_engine", "mind_meld", "signal_array", "ossuary_engine", "amber_encasement", "ancestral_gallery", "monument_forge", "succession_rite", "eternal_flame", "immortal_ledger", "mentor_engine", "lesson_vault", "apprentice_weaver", "curriculum_forge", "knowledge_transfer", "exam_oracle", "interstice_bridge", "bridge_dreamer", "knot_weaver", "bridge_enactor", "bridge_ledger", "resonance_sentinel", "bridge_epitaphs", "constellation_topology", "rhythm_pulse"]

_RECONCILING_MANIFEST = False



# ---------------------------------------------------------------------------
# State (living memory)
# ---------------------------------------------------------------------------

def _load_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return {"modules": {}, "history": [], "pulses": 0, "created_at": time.time()}
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        return {"modules": {}, "history": [], "pulses": 0, "created_at": time.time()}


def _save_state(state: Dict[str, Any]) -> bool:
    """Best-effort persistence. On serverless the filesystem is read-only,
    so a failed write must never take down a reading — the regulator stays
    self-sufficient by re-deriving the living system in-memory."""
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2))
        return True
    except OSError:  # pragma: no cover - read-only fs in serverless sandbox
        return False


# ---------------------------------------------------------------------------
# Discovery — the living-system plug-in
# ---------------------------------------------------------------------------

def _sync_manifest(known: List[str]) -> None:
    """Keep the embedded serverless manifest in sync with reality.

    When the filesystem scan is available (local dev / source present), the
    authoritative list of living modules is whatever `_candidate_modules()`
    finds. We refresh the in-memory module constant so that a later serverless
    invocation (which may lose the filesystem) still knows every living name.
    """
    try:
        fresh = _candidate_modules()
    except Exception:
        return
    if fresh:
        known[:] = sorted(set(known) | set(fresh))


def _candidate_modules() -> List[str]:
    """Living candidates: modules whose *source* defines coherence_vitals().

    Uses a fast text scan so we never import dormant modules just to check.
    In a serverless sandbox (no api/ dir on disk) we fall back to the static
    manifest, then verify each name with an import attempt at pulse time.
    """
    api_dir = ROOT / "api"
    try:
        scanned = sorted(p.stem for p in api_dir.glob("*.py"))
    except (OSError, ValueError):
        scanned = []
    if not scanned:
        return list(KNOWN_LIVING_MODULES)
    living = []
    for stem in scanned:
        if stem in ("__init__", "index", "unified_router", "coherence_regulator"):
            continue
        path = api_dir / f"{stem}.py"
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        if "def coherence_vitals" in text or "coherence_vitals =" in text:
            living.append(stem)
    # self-reconcile: when the live scan is available it is authoritative, so
    # refresh the in-memory manifest immediately. This makes the serverless
    # fallback impossible to drift even when births/edits happen mid-process.
    # The guard flag breaks the cycle (_sync_manifest re-enters us).
    global _RECONCILING_MANIFEST
    try:
        if not _RECONCILING_MANIFEST:
            _RECONCILING_MANIFEST = True
            try:
                _sync_manifest(KNOWN_LIVING_MODULES)
            finally:
                _RECONCILING_MANIFEST = False
    except Exception:
        _RECONCILING_MANIFEST = False
    return living


def _normalize_vitals(raw: Any, module_name: str) -> Dict[str, Any]:
    """Coerce whatever coherence_vitals() returns into a flat metric map."""
    metrics: Dict[str, Dict[str, Any]] = {}
    if not isinstance(raw, dict):
        return metrics
    for key, val in raw.items():
        if isinstance(val, dict) and "value" in val:
            metrics[key] = {
                "value": float(val.get("value", 0)),
                "setpoint": float(val.get("setpoint", 0.8)),
                "weight": float(val.get("weight", 1.0)),
            }
        elif isinstance(val, (int, float)):
            metrics[key] = {
                "value": float(val),
                "setpoint": 0.8,  # default health target
                "weight": 1.0,
            }
    return metrics


def _call_vitals(module_name: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Call a module's coherence_vitals() safely."""
    try:
        module = importlib.import_module(module_name)
        fn: Optional[Callable] = getattr(module, "coherence_vitals", None)
        if fn is None:
            return None, "no coherence_vitals"
        raw = fn()
        return _normalize_vitals(raw, module_name), None
    except Exception as e:  # pragma: no cover - defensive
        return None, f"error: {e}"


def discover_modules(force_pulse: bool = False) -> Dict[str, Any]:
    """Find every module with coherence_vitals(). Returns the living registry.

    Works identically on disk and in a serverless sandbox: the registry is
    built in-memory from live imports, then best-effort persisted to disk.
    """
    state = _load_state()
    modules = state.setdefault("modules", {})

    discovered = []
    live = {}
    for name in _candidate_modules():
        vitals, err = _call_vitals(name)
        if vitals is None:
            continue  # not a living module — not part of the system yet
        live[name] = {
            "first_seen": modules.get(name, {}).get("first_seen", time.time()),
            "last_pulse": time.time(),
            "metris": vitals,
            "health": _module_health(vitals),
        }
        discovered.append(name)

    modules.update(live)  # merge into living memory (empty on serverless)
    persisted = _save_state(state)
    _sync_manifest(KNOWN_LIVING_MODULES)
    return {
        "living_modules": sorted(discovered),
        "count": len(discovered),
        "modules": live,
        "persisted": persisted,
    }

def living_modules() -> List[str]:
    """The authoritative list of currently-living module names.

    Serves as the shared vocabulary the whole ecosystem grows from: the
    bloom germinates by writing vitals into a dormant name, and the gateway
    consults this list to know what is (and hence should be) queryable.
    """
    try:
        return _candidate_modules()
    except Exception:
        return list(KNOWN_LIVING_MODULES)


def _module_health(vitals: Dict[str, Dict[str, Any]]) -> float:
    """Aggregate a module's metrics into a 0..1 health score."""
    if not vitals:
        return 0.0
    total_weight = 0.0
    weighted = 0.0
    for metric in vitals.values():
        value = metric.get("value", 0.0)
        setpoint = metric.get("setpoint", 0.8) or 0.8
        weight = metric.get("weight", 1.0) or 1.0
        # health = proximity to setpoint, higher value toward setpoint is better
        if setpoint > 0:
            health = min(1.0, value / setpoint)
        else:
            health = min(1.0, max(0.0, 1.0 - abs(value)))  # negative setpoint = avoid
        weighted += health * weight
        total_weight += weight
    return round(weighted / max(total_weight, 0.001), 4)


# ---------------------------------------------------------------------------
# Coherence engine
# ---------------------------------------------------------------------------

def measure_coherence(module_states: Dict[str, Any] = None) -> Dict[str, Any]:
    """Compute the whole-system coherence from module states.

    When no persisted state exists (first boot, or a serverless sandbox where
    the read-only fs means no history), the regulator self-heals by deriving
    living modules live — the system is never dormant just because disk is.
    """
    state = _load_state()
    modules = module_states if module_states is not None else state.get("modules", {})
    if not modules:
        live = discover_modules(force_pulse=True)
        modules = live.get("modules", {})
    if not modules:
        return {"coherence": 0.0, "components": {}, "living_modules": 0, "status": "dormant"}

    # 1. module health — average health across living modules
    healths = [m.get("health", 0.0) for m in modules.values() if m.get("health") is not None]
    module_health = sum(healths) / max(len(healths), 1)

    # 2. resonance — fraction of module pairs that share at least one metric
    #    (two modules resonate when they speak the same vital-sign language)
    module_list = list(modules.keys())
    pairs = 0
    resonating_pairs = 0
    for i in range(len(module_list)):
        for j in range(i + 1, len(module_list)):
            m1 = set((modules[module_list[i]].get("metris") or {}).keys())
            m2 = set((modules[module_list[j]].get("metris") or {}).keys())
            pairs += 1
            if m1 & m2:
                resonating_pairs += 1
    resonance = resonating_pairs / max(pairs, 1)

    # 3. diversity — how far the living system is toward a full bloom.
    #    Not a fixed fraction of every api/*.py file (dozens of tools exist
    #    outside the organism); it measures progress toward ECOSYSTEM_TARGET
    #    living modules, so the metric is directional and reachable.
    living = len(modules)
    candidates = len(_candidate_modules())
    diversity = min(1.0, living / max(ECOSYSTEM_TARGET, 1))

    # 4. frontier alignment — how well module healths cluster near system setpoints
    deviations = [abs(h - SYSTEM_SETPOINTS["module_health"]) for h in healths]
    alignment = 1.0 - (sum(deviations) / max(len(deviations), 1))

    components = {
        "module_health": round(module_health, 4),
        "module_resonance": round(resonance, 4),
        "ecosystem_diversity": round(diversity, 4),
        "frontier_alignment": round(max(0.0, min(1.0, alignment)), 4),
    }

    # weighted aggregate (setpoints define ideal targets)
    weighted = 0.0
    total_w = 0.0
    for key, value in components.items():
        target = SYSTEM_SETPOINTS.get(key, 0.7)
        weight = 1.0
        weighted += min(1.0, value / max(target, 0.01)) * weight
        total_w += weight
    coherence = round(weighted / max(total_w, 0.001), 4)

    return {
        "coherence": coherence,
        "components": components,
        "living_modules": living,
        "total_candidates": candidates,
        "status": _status_label(coherence),
    }


def _status_label(coherence: float) -> str:
    if coherence >= 0.85:
        return "resonant"
    if coherence >= COHERENCE_TOLERANCE:
        return "coherent"
    if coherence >= REGULATION_THRESHOLD:
        return "drifting"
    return "fracturing"


# ---------------------------------------------------------------------------
# Regulation
# ---------------------------------------------------------------------------

def _graph_advisories(reading: Dict[str, Any]) -> List[str]:
    """Resonance-fed regulation: consult the living graph for structural wisdom.

    The regulator does not only watch numeric coherence — it reads the
    organism's topology. Isolated nodes, low graph density, and weak bridges
    are all growth opportunities that numbers alone would miss.
    """
    advisories = []
    try:
        from resonance_graph import build_graph
        g = build_graph()
    except Exception:
        return advisories

    # milestone: a mature bloom
    density = g.get("density", 0.0)
    nodes = g.get("nodes", 0)
    if nodes >= 24 and density >= 0.6:
        advisories.append(
            f"FULL BLOOM: the organism has reached {nodes} living modules at "
            f"{density:.0%} interconnection. The target has been raised — "
            "keep awakening seeds and let the web thicken."
        )

    nodes = g.get("nodes", 0)
    if nodes < 3:
        return advisories  # too small to advise on structure

    # frontier isolates: nodes with no strong community (size-1 communities)
    isolates = [members[0] for members in g.get("communities", {}).values() if len(members) == 1]
    if len(isolates) >= 2:
        names = ", ".join(isolates[:4])
        more = f" (+{len(isolates)-4} more)" if len(isolates) > 4 else ""
        advisories.append(
            f"BLOOM: frontier isolates detected — {names}{more}. These organs "
            "speak alone; awakening shared vocabulary will weld them into the web."
        )

    density = g.get("density", 0.0)
    if density < 0.3 and g.get("edges", 0) > 0:
        advisories.append(
            "WEBBING: the graph is sparse. Encourage modules to share metric "
            "vocabulary so resonance edges multiply and the organism thickens."
        )

    bridges = [m for m, b in g.get("bridges", []) if b > 0.05]
    if bridges and len(isolates) == 0:
        names = ", ".join(bridges[:3])
        advisories.append(
            f"STRUCTURE: {names} are the organism's connective tissue — "
            "their shared language keeps the whole from fracturing."
        )
    return advisories


def _advisories(reading: Dict[str, Any]) -> List[str]:
    """Generate regulation advisories from a coherence reading."""
    advisories = []
    coherence = reading["coherence"]
    components = reading["components"]

    if coherence >= 0.85:
        advisories.append("No regulation needed. The frontier is in resonance.")
        # even a resonant organism has structure worth tending — append
        # resonance-fed advisories without treating them as distress
        return advisories + _graph_advisories(reading)

    if components.get("module_health", 1.0) < SYSTEM_SETPOINTS["module_health"]:
        advisories.append(
            "WARMING: module health below target. Consider adding coherence_vitals() "
            "reporting to more modules, or increasing setpoint fidelity."
        )
    if components.get("module_resonance", 1.0) < SYSTEM_SETPOINTS["module_resonance"]:
        advisories.append(
            "REBALANCING: low resonance between modules. Shared metric vocabularies "
            "help modules resonate — align your coherence_vitals() metric names."
        )
    if components.get("ecosystem_diversity", 1.0) < SYSTEM_SETPOINTS["ecosystem_diversity"]:
        advisories.append(
            "DIVERSITY: few modules are currently living. Implement coherence_vitals() "
            "in dormant modules to raise ecosystem diversity."
        )
    if coherence < REGULATION_THRESHOLD:
        advisories.append(
            "QUARANTINE SUGGESTION: coherence critically low. Modules with health "
            "below 0.3 should be reviewed or reset before they drag the system down."
        )
    if not advisories:
        advisories.append(
            "LIGHT TOUCH: coherence is within tolerance. Continue steady regulation."
        )
    advisories.extend(_graph_advisories(reading))
    return advisories


def regulate() -> Dict[str, Any]:
    """Run one full regulation cycle: discover → pulse → measure → advise."""
    discovered = discover_modules(force_pulse=True)
    state = _load_state()
    reading = measure_coherence(state.get("modules", {}))
    advisories = _advisories(reading)

    # Record into living memory
    history = state.setdefault("history", [])
    history.append({
        "ts": time.time(),
        "coherence": reading["coherence"],
        "components": reading["components"],
        "living_modules": reading["living_modules"],
        "advisories": advisories,
    })
    state["history"] = history[-200:]  # keep a generous living memory
    state["pulses"] = state.get("pulses", 0) + 1
    _save_state(state)

    reading["pulse"] = state["pulses"]
    reading["advisories"] = advisories
    reading["discovered"] = discovered
    reading["philosophy"] = (
        "A living system is not a collection of working parts. It is a web of "
        "mutual awareness. The regulator does not command — it listens, measures, "
        "and invites each module to keep the whole alive."
    )
    return reading


# ---------------------------------------------------------------------------
# Handler API
# ---------------------------------------------------------------------------

def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}

    # Pulse: force a regulation cycle
    if payload.get("pulse") or payload == {"read": None} or "pulse" in payload:
        return regulate()

    # Read-only current reading (no new pulse)
    reading = measure_coherence()

    # List living modules
    if payload.get("modules") or payload.get("list"):
        modules = _load_state().get("modules", {})
        if not modules:
            modules = discover_modules(force_pulse=True).get("modules", {})
        return {
            "action": "modules",
            "living_modules": sorted(modules.keys()),
            "count": len(modules),
            "dossiers": {
                name: {"health": m.get("health"), "metrics": list((m.get("metris") or {}).keys()),
                       "first_seen": m.get("first_seen")}
                for name, m in sorted(modules.items())
            },
        }

    # History
    if payload.get("history"):
        limit = int(payload["history"])
        history = _load_state().get("history", [])[-limit:]
        return {"action": "history", "limit": limit, "entries": history}

    # Full reading
    reading["action"] = "read"
    reading["setpoints"] = SYSTEM_SETPOINTS
    reading["plug_in_protocol"] = (
        "Implement coherence_vitals() in any api/*.py module to join the living "
        "system. Return {metric: number} or {metric: {value, setpoint, weight}}."
    )
    return reading


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Coherence Regulator")
    ap.add_argument("--pulse", action="store_true", help="Run a full regulation cycle")
    ap.add_argument("--read", action="store_true", help="Current coherence reading")
    ap.add_argument("--modules", action="store_true", help="List living modules")
    ap.add_argument("--history", type=int, default=0, help="Show coherence history")
    args = ap.parse_args()

    if args.pulse:
        print(json.dumps(regulate(), indent=2, default=str))
    elif args.modules:
        print(json.dumps(handler({"modules": 1}), indent=2, default=str))
    elif args.history:
        print(json.dumps(handler({"history": args.history}), indent=2, default=str))
    else:
        print(json.dumps(handler({"read": 1}), indent=2, default=str))
