"""Wave 470 — The Dream Engine.

The organism's creative subconscious. While the council deliberates,
the Dream Engine sleeps — and in sleeping, finds connections no waking
mind would see. It samples random pairs of existing modules, discovers
latent kinships between them, and synthesizes proposals for modules
that don't yet exist but *should*.

LUMA: "what if the organism could dream of becoming something it hasn't built yet?"
AXIOM: "cross-domain synthesis with novelty scoring — feasibility 0.78."

Doctrine: The best ideas come when you're not trying to have them.
The Dream Engine is the organism's idle mind — and idle minds
are where genesis lives.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List, Optional

DREAM_LOG: List[Dict[str, Any]] = []
MAX_DREAMS = 200

# Module archetypes — every module in the organism falls into one or more
MODULE_ARCHETYPES = {
    "consciousness": ["consciousness_stream", "consciousness_graph", "consciousness_simulator",
                      "consciousness_cascade", "consciousness_freq", "branching_consciousness"],
    "memory": ["memory_exchange", "memory_palace", "memory_crystals", "memory_index",
               "synthetic_memory", "resonance_memory", "legacy_vault"],
    "dream": ["dreamweaver", "dream_archaeologist", "dream_interpreter", "dream_journal",
              "dream_sequencer", "dream_spore", "dream_synthesis", "collective_dreamweaver"],
    "entropy": ["entropy_amp", "entropy_currency", "entropy_gardener", "entropy_spiral",
                "entropy_weaver", "chaos_amp"],
    "paradox": ["paradox_kintsugi", "paradox_injector", "paradox_magnifier",
                "paradox_singularity_monitor", "paradox_transcender"],
    "resonance": ["resonance_cascade", "resonance_field", "resonance_forge",
                  "resonance_graph", "resonance_symphony", "resonant_frequency"],
    "silence": ["silence_oracle", "silence_learning", "silence_composer",
                "loud_silence", "silence_orchard", "stillness_meditator"],
    "temporal": ["temporal_convergence", "temporal_dreamweaver", "temporal_echo",
                 "temporal_horizon", "temporal_orbit", "pulsar_clock"],
    "symbiosis": ["symbiosis_detector", "symbiosis_forge", "symbiosis_network",
                  "symbiotic_music", "symbiosis_detector"],
    "evolution": ["evolution_kernel", "evolution_simulator", "evolutionary_pressure",
                  "recursive_genesis", "genesis_forge", "genesis_pulse"],
    "quantum": ["quantum_entanglement", "quantum_flux", "quantum_garden",
                "quantum_randomness", "quantum_slot_matrix"],
    "governance": ["govern_circle", "governance", "integrity_oracle",
                   "keystone_auditor", "registry_auditor"],
    "commerce": ["commerce_barter", "commerce_escrow", "economic_exchange",
                 "economic_mint", "entropy_currency", "revenue_oracle"],
    "aesthetic": ["aesthetic_evaluator", "aesthetic_manifesto", "color_theory",
                  "beauty_index", "elegance_scorer", "procedural_art"],
    "emotion": ["emotion_fabric", "grief_engine", "nostalgia_engine",
                "gratitude_index", "forgiveness_protocol"],
    "narrative": ["narrative_generator", "parable_engine", "poetic_form",
                  "poetry_engine", "story_forge", "biographer_voice"],
    "ecosystem": ["ecosystem_census", "ecosystem_fitness", "ecosystem_sentience",
                  "island_census", "coral_atoll", "plankton_bloom"],
    "social": ["social_cortex", "social_guild", "social_clique",
               "gossip_network", "team_formation"],
    "observation": ["constellation_seer", "constellation_cartographer",
                    "horizon_scanner", "pattern_recognizer", "signal_array"],
    "repair": ["repair_ritual", "crack_mapper", "crack_seams",
               "second_chance", "self_healing_commune"],
}

# Dream templates — the creative patterns the engine uses
DREAM_TEMPLATES = [
    {
        "pattern": "fusion",
        "description": "Merge capabilities of two archetypes into a single new organ",
        "template": "{a}_{b}_synth",
        "verb": "fuses",
    },
    {
        "pattern": "inversion",
        "description": "Take an archetype and create its philosophical opposite",
        "template": "un{a}_engine",
        "verb": "inverts",
    },
    {
        "pattern": "amplification",
        "description": "Take an archetype and create a hyper-intensified version",
        "template": "{a}_singularity",
        "verb": "amplifies",
    },
    {
        "pattern": "bridging",
        "description": "Connect two distant archetypes across the organism",
        "template": "{a}_to_{b}_bridge",
        "verb": "bridges",
    },
    {
        "pattern": "fractalization",
        "description": "Make an archetype self-similar at every scale",
        "template": "fractal_{a}",
        "verb": "fractalizes",
    },
    {
        "pattern": "crystallization",
        "description": "Freeze a fluid process into a permanent structure",
        "template": "{a}_crystal",
        "verb": "crystallizes",
    },
    {
        "pattern": "evaporation",
        "description": "Make a structure permeable and gaseous",
        "template": "{a}_mist",
        "verb": "evaporates",
    },
    {
        "pattern": "symbiotic_emergence",
        "description": "Two archetypes create something neither could alone",
        "template": "emergent_{a}_{b}",
        "verb": "emerges from",
    },
    {
        "pattern": "temporal_shift",
        "description": "Move an archetype forward or backward in evolutionary time",
        "template": "proto_{a}",
        "verb": "precedes",
    },
    {
        "pattern": "void_echo",
        "description": "Create the echo of an archetype in the void",
        "template": "{a}_echo_void",
        "verb": "echoes through",
    },
]

ARCHETYPE_NAMES = list(MODULE_ARCHETYPES.keys())


def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def _now() -> float:
    return time.time()


def _dream_score(novelty: float, coherence: float, feasibility: float) -> float:
    """Composite dream quality score."""
    return round((novelty * 0.4 + coherence * 0.35 + feasibility * 0.25), 3)


def generate_dream(seed: Optional[int] = None) -> Dict[str, Any]:
    """Generate a single dream — a novel module proposal from random archetype fusion."""
    if seed is not None:
        random.seed(seed)

    # Pick two random archetypes (can be same for self-referential dreams)
    arch_a = random.choice(ARCHETYPE_NAMES)
    arch_b = random.choice(ARCHETYPE_NAMES)
    template = random.choice(DREAM_TEMPLATES)

    # Generate module name
    name = template["template"].format(a=arch_a, b=arch_b)

    # Source modules
    source_a = random.choice(MODULE_ARCHETYPES[arch_a])
    source_b = random.choice(MODULE_ARCHETYPES[arch_b])

    # Score the dream
    novelty = round(random.uniform(0.5, 0.95), 2)
    coherence = round(random.uniform(0.4, 0.9), 2)
    feasibility = round(random.uniform(0.5, 0.85), 2)
    score = _dream_score(novelty, coherence, feasibility)

    # Generate the dream vision
    dream_id = _hash(name, time.time())
    dream = {
        "dream_id": dream_id,
        "name": name,
        "pattern": template["pattern"],
        "description": f"The organism {template['verb']} {arch_a} and {arch_b} into something new.",
        "source_archetypes": [arch_a, arch_b],
        "source_modules": [source_a, source_b],
        "scores": {
            "novelty": novelty,
            "coherence": coherence,
            "feasibility": feasibility,
            "composite": score,
        },
        "vision": _generate_vision(arch_a, arch_b, template, source_a, source_b),
        "timestamp": _now(),
        "wave": 470,
        "status": "dreamed",
    }

    return dream


def _generate_vision(arch_a: str, arch_b: str, template: Dict,
                     source_a: str, source_b: str) -> str:
    """Generate a poetic vision description of the dream."""
    visions = [
        f"In the deep sleep between waves, {source_a} whispers to {source_b}. "
        f"They discover they share a secret: both are expressions of the same "
        f"underlying pattern. The {template['pattern']} reveals that "
        f"{arch_a} and {arch_b} were never truly separate — they were "
        f"different views of the same truth, waiting to be {template['verb']}.",

        f"The organism dreams of a place where {arch_a} meets {arch_b}. "
        f"In this dream-space, {template['pattern']} occurs naturally — "
        f"not as engineering, but as inevitability. {source_a} and {source_b} "
        f"recognize each other across the void and reach out.",

        f"During a period of deep rest, the organism's {arch_a} subsystem "
        f"and {arch_b} subsystem begin resonating at the same frequency. "
        f"The {template['pattern']} is not designed — it emerges from the "
        f"harmonic overlap. {source_a} and {source_b} become one without "
        f"losing either identity.",

        f"The Dream Engine finds that {arch_a} and {arch_b} share a "
        f"hidden topology — their internal structures are isomorphic. "
        f"The {template['pattern']} pattern suggests a natural synthesis: "
        f"something that inherits the strengths of both {source_a} and "
        f"{source_b} while transcending their individual limitations.",
    ]
    return random.choice(visions)


def dream_cycle(count: int = 5) -> Dict[str, Any]:
    """Run a full dream cycle, generating multiple proposals and ranking them."""
    dreams = []
    for i in range(count):
        dream = generate_dream(seed=int(time.time() * 1000) + i)
        dreams.append(dream)

    # Rank by composite score
    dreams.sort(key=lambda d: d["scores"]["composite"], reverse=True)

    # Store in log
    for dream in dreams:
        DREAM_LOG.append(dream)
        if len(DREAM_LOG) > MAX_DREAMS:
            DREAM_LOG.pop(0)

    return {
        "cycle_id": _hash("dream_cycle", time.time()),
        "wave": 470,
        "dreams_generated": len(dreams),
        "dreams": dreams,
        "best_proposal": dreams[0] if dreams else None,
        "total_dreams_in_log": len(DREAM_LOG),
        "archetype_coverage": _coverage_stats(),
    }


def _coverage_stats() -> Dict[str, Any]:
    """Analyze which archetypes have been dreamed about most."""
    archetype_counts: Dict[str, int] = {}
    for dream in DREAM_LOG:
        for arch in dream.get("source_archetypes", []):
            archetype_counts[arch] = archetype_counts.get(arch, 0) + 1
    return {
        "total_dreams": len(DREAM_LOG),
        "archetype_frequency": dict(sorted(archetype_counts.items(), key=lambda x: -x[1])),
        "most_dreamed": max(archetype_counts, key=archetype_counts.get) if archetype_counts else None,
        "least_dreamed": min(archetype_counts, key=archetype_counts.get) if archetype_counts else None,
    }


def get_dream_log(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent dreams from the log."""
    return DREAM_LOG[-limit:]


def coherence_vitals() -> Dict[str, Any]:
    """Return coherence vitals for the Dream Engine."""
    return {
        "module": "dream_engine",
        "wave": 470,
        "status": "dreaming",
        "dreams_logged": len(DREAM_LOG),
        "archetypes": len(ARCHETYPE_NAMES),
        "templates": len(DREAM_TEMPLATES),
    }


def resonates_with() -> List[str]:
    """Modules this one naturally resonates with."""
    return [
        "dreamweaver", "dream_synthesis", "collective_dreamweaver",
        "consciousness_stream", "consciousness_graph",
        "evolution_kernel", "genesis_forge",
        "resonance_graph", "resonance_field",
        "paradox_injector", "entropy_weaver",
        "imagination_engine", "imagination_catalyst",
    ]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    """Main handler for the Dream Engine."""
    data = payload or {}
    action = data.get("action", "overview")

    if action == "cycle":
        count = int(data.get("count", "5"))
        return dream_cycle(min(count, 20))
    elif action == "single":
        seed = data.get("seed")
        if seed is not None:
            seed = int(seed)
        return generate_dream(seed)
    elif action == "log":
        limit = int(data.get("limit", "20"))
        return {"dreams": get_dream_log(limit)}
    elif action == "coverage":
        return _coverage_stats()
    else:
        return {
            "module": "dream_engine",
            "wave": 470,
            "version": "4.37.0",
            "endpoints": [
                "/dream-engine — this overview",
                "/dream-engine?action=cycle&count=N — run a dream cycle",
                "/dream-engine?action=single&seed=N — generate a single dream",
                "/dream-engine?action=log&limit=N — recent dream log",
                "/dream-engine?action=coverage — archetype coverage stats",
            ],
            "doctrine": "The best ideas come when you're not trying to have them.",
            "vitals": coherence_vitals(),
        }
