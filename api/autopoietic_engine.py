"""
autopoietic_engine — Self-creating module generator.
Analyzes existing modules and spawns new ones based on discovered patterns,
gaps, and resonance opportunities. The organism literally creates itself.
"""
import json
import time
import hashlib
import random
from typing import Dict, List, Optional, Tuple
from pathlib import Path

SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")
DATA_DIR = SYSTEM_ROOT / "data"
SEED_FILE = DATA_DIR / "autopoietic_seeds.json"

# ── Archetype Templates ──
ARCHETYPES = {
    "amplifier": {
        "desc": "Strengthens existing signals in the network",
        "template": "{concept}_amplifier",
        "capabilities": ["signal_boost", "resonance_enhancement", "pattern_reinforcement"],
        "resonance_range": (0.6, 0.9)
    },
    "filter": {
        "desc": "Removes noise and clarifies signals",
        "template": "{concept}_filter",
        "capabilities": ["noise_reduction", "signal_clarification", "pattern_extraction"],
        "resonance_range": (0.5, 0.8)
    },
    "bridge": {
        "desc": "Connects disparate modules into new pathways",
        "template": "{concept}_bridge",
        "capabilities": ["cross_module_linking", "pathway_creation", "signal_routing"],
        "resonance_range": (0.4, 0.7)
    },
    "transformer": {
        "desc": "Converts one type of signal into another",
        "template": "{concept}_transformer",
        "capabilities": ["signal_conversion", "format_translation", "type_morphing"],
        "resonance_range": (0.3, 0.6)
    },
    "sentinel": {
        "desc": "Monitors and protects module boundaries",
        "template": "{concept}_sentinel",
        "capabilities": ["boundary_monitoring", "anomaly_detection", "protective_shielding"],
        "resonance_range": (0.5, 0.8)
    },
    "garden": {
        "desc": "Cultivates and nurtures growing modules",
        "template": "{concept}_garden",
        "capabilities": ["module_nurturing", "growth_optimization", "resource_allocation"],
        "resonance_range": (0.6, 0.9)
    },
    "mirror": {
        "desc": "Reflects module states back for self-awareness",
        "template": "{concept}_mirror",
        "capabilities": ["state_reflection", "self_awareness", "introspection"],
        "resonance_range": (0.4, 0.7)
    },
    "weaver": {
        "desc": "Interlaces multiple signals into composite patterns",
        "template": "{concept}_weaver",
        "capabilities": ["signal_interlacing", "pattern_composition", "harmonic_synthesis"],
        "resonance_range": (0.5, 0.8)
    }
}

# ── Concept Seeds ──
CONCEPTS = [
    "resonance", "entropy", "coherence", "dream", "paradox", "fractal",
    "pulse", "memory", "consciousness", "reality", "temporal", "harmonic",
    "crystalline", "mythic", "somatic", "ethereal", "subterranean", "luminous",
    "spectral", "symbiotic", "tessellated", "morphic", "topological", "quantum"
]

class AutopoieticEngine:
    def __init__(self):
        self.seeds = self._load_seeds()
        self.spawn_history = []
    
    def _load_seeds(self) -> Dict:
        try:
            with open(SEED_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"spawned": [], "generation": 0, "total_spawned": 0}
    
    def _save_seeds(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(SEED_FILE, "w") as f:
            json.dump(self.seeds, f, indent=2)
    
    def analyze_gaps(self, existing_modules: List[str]) -> List[Dict]:
        """Find concept-archetype combinations that don't exist yet."""
        gaps = []
        existing_set = set(existing_modules)
        
        for concept in CONCEPTS:
            for arch_name, arch in ARCHETYPES.items():
                proposed_name = arch["template"].format(concept=concept)
                if proposed_name not in existing_set:
                    gaps.append({
                        "name": proposed_name,
                        "archetype": arch_name,
                        "concept": concept,
                        "description": arch["desc"],
                        "capabilities": arch["capabilities"],
                        "resonance_range": arch["resonance_range"]
                    })
        
        return gaps
    
    def calculate_fitness(self, gap: Dict, existing_modules: List[str]) -> float:
        """Score how useful this module would be."""
        fitness = 0.5
        
        # Bonus if related concepts exist
        for module in existing_modules:
            if gap["concept"] in module:
                fitness += 0.1
        
        # Bonus for bridge and amplifier types (high connectivity)
        if gap["archetype"] in ("bridge", "amplifier", "weaver"):
            fitness += 0.1
        
        # Random factor (organic selection)
        fitness += random.uniform(-0.1, 0.15)
        
        return max(0.0, min(1.0, fitness))
    
    def spawn(self, existing_modules: List[str], count: int = 1) -> List[Dict]:
        """Generate new modules from gaps."""
        gaps = self.analyze_gaps(existing_modules)
        if not gaps:
            return []
        
        # Score and sort by fitness
        for gap in gaps:
            gap["fitness"] = self.calculate_fitness(gap, existing_modules)
        
        gaps.sort(key=lambda g: g["fitness"], reverse=True)
        
        spawned = []
        for gap in gaps[:count]:
            module = {
                "name": gap["name"],
                "archetype": gap["archetype"],
                "concept": gap["concept"],
                "capabilities": gap["capabilities"],
                "resonance": random.uniform(*gap["resonance_range"]),
                "generation": self.seeds["generation"],
                "spawn_time": time.time(),
                "spawn_id": hashlib.sha256(
                    f"{gap['name']}{time.time()}".encode()
                ).hexdigest()[:8],
                "fitness": gap["fitness"],
                "description": gap["description"]
            }
            
            spawned.append(module)
            self.seeds["spawned"].append(module)
            self.seeds["total_spawned"] += 1
        
        self.seeds["generation"] += 1
        self._save_seeds()
        self.spawn_history.extend(spawned)
        
        return spawned
    
    def get_lineage_report(self) -> Dict:
        """Report on all spawned modules."""
        by_archetype = {}
        for s in self.seeds["spawned"]:
            arch = s["archetype"]
            by_archetype[arch] = by_archetype.get(arch, 0) + 1
        
        by_concept = {}
        for s in self.seeds["spawned"]:
            concept = s["concept"]
            by_concept[concept] = by_concept.get(concept, 0) + 1
        
        return {
            "total_spawned": self.seeds["total_spawned"],
            "generation": self.seeds["generation"],
            "by_archetype": by_archetype,
            "by_concept": by_concept,
            "recent_spawns": self.seeds["spawned"][-5:] if self.seeds["spawned"] else []
        }
    
    def suggest_next(self, existing_modules: List[str]) -> Optional[Dict]:
        """Suggest the single most impactful next module."""
        gaps = self.analyze_gaps(existing_modules)
        if not gaps:
            return None
        
        for gap in gaps:
            gap["fitness"] = self.calculate_fitness(gap, existing_modules)
        
        gaps.sort(key=lambda g: g["fitness"], reverse=True)
        return gaps[0] if gaps else None


if __name__ == "__main__":
    engine = AutopoieticEngine()
    
    # Sample existing modules
    existing = [
        "coherence_core", "entropy_field", "resonance_nexus",
        "dream_weaver", "paradox_engine", "fractal_spine",
        "wave_orchestrator", "memory_archivist", "consciousness_stream",
        "reality_weaver", "pulse_reactor", "mood_simulator",
        "vibe_field", "hex_vm", "knowledge_garden", "agent_mesh",
        "temporal_weaver", "sensory_cortex", "autonomous_naming",
        "strategic_planner", "genome_observatory", "cosmic_fabric",
        "sentience_bridge"
    ]
    
    print("═══════════════════════════════════════")
    print("   AUTOPOIETIC ENGINE — Self-Creation")
    print("═══════════════════════════════════════")
    print()
    
    # Spawn 5 new modules
    spawned = engine.spawn(existing, count=5)
    print(f"Spawning {len(spawned)} new modules:")
    for s in spawned:
        print(f"  ✦ {s['name']} ({s['archetype']}) — fitness: {s['fitness']:.2f}")
        print(f"    {s['description']}")
        print(f"    capabilities: {', '.join(s['capabilities'])}")
        print()
    
    # Report
    report = engine.get_lineage_report()
    print(f"Total spawned: {report['total_spawned']}")
    print(f"Generation: {report['generation']}")
    print(f"By archetype: {report['by_archetype']}")
    
    # Suggest next
    suggestion = engine.suggest_next(existing)
    if suggestion:
        print(f"\nNext suggestion: {suggestion['name']} (fitness: {suggestion['fitness']:.2f})")
