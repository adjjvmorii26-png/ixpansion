"""Organism Orchestrator Configuration."""

# Configuration for the organism orchestrator
ORCHESTRATOR_CONFIG = {
    "default_coherence_threshold": 0.5,
    "max_waves": 100,
    "default_persona": {
        "curiosity": 0.5,
        "creativity": 0.5,
        "risk_aversion": 0.5,
        "cooperation": 0.5,
        "exploration": 0.5,
    },
    "wave_evolution_rate": 0.05,
    "module_evolution_rate": 0.01,
    "persona_evolution_rate": 0.02,
    "enable_dream_integration": True,
    "enable_persona_evolution": True,
    "enable_coherence_tracking": True,
}

# Wave progression settings
WAVE_PROGRESSION = {
    "wave_1_foundational": {"coherence_gain": 0.1, "modules_added": 5},
    "wave_2_expansion": {"coherence_gain": 0.15, "modules_added": 8},
    "wave_3_consolidation": {"coherence_gain": 0.12, "modules_added": 6},
    "wave_4_transformation": {"coherence_gain": 0.18, "modules_added": 10},
    "wave_5_stabilization": {"coherence_gain": 0.1, "modules_added": 4},
}

# Dimension settings
DIMENSIONS = {
    "cognitive": {"weight": 0.3, "description": "Thinking and reasoning modules"},
    "emotional": {"weight": 0.25, "description": "Feeling and empathy modules"},
    "creative": {"weight": 0.2, "description": "Innovation and generation modules"},
    "social": {"weight": 0.15, "description": "Interaction and cooperation modules"},
    "sensory": {"weight": 0.1, "description": "Perception and perception modules"},
}
