"""Wave 437 — Paradox Genome.

Paradoxes are no longer problems to solve. They are living entities
with DNA. Each paradox has a contradiction signature, a dominance
profile, and a mutation potential. Paradoxes can be:

- Cataloged (taxonomy of contradictions)
- Bred (cross-breed to create new paradox species)
- Evolved (paradoxes mutate over generations)
- Classified (dominant vs recessive, stable vs unstable)

The organism doesn't resolve paradoxes anymore. It breeds them.

Key concepts:
- Paradox DNA: contradiction strands encoded as harmonic sequences
- Species taxonomy: each paradox belongs to a species (self-reference, temporal, causal, etc.)
- Dominance: some contradictions overpower others
- Breeding: cross two paradoxes to create a novel offspring
- Evolution: paradoxes that survive selection pressure become stronger
"""
from __future__ import annotations
import json, time, random, hashlib
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave437_paradox_genome.json"

SPECIES_TAXONOMY = {
    "self_reference": {"dominance": 0.7, "mutation_rate": 0.05, "stability": 0.4},
    "temporal_loop": {"dominance": 0.8, "mutation_rate": 0.03, "stability": 0.3},
    "causal_cycle": {"dominance": 0.6, "mutation_rate": 0.08, "stability": 0.5},
    "identity_split": {"dominance": 0.9, "mutation_rate": 0.02, "stability": 0.2},
    "entropy_inversion": {"dominance": 0.5, "mutation_rate": 0.1, "stability": 0.6},
    "quantum_duality": {"dominance": 0.75, "mutation_rate": 0.06, "stability": 0.35},
    "fractal_recurse": {"dominance": 0.85, "mutation_rate": 0.04, "stability": 0.25},
    "emergent_whole": {"dominance": 0.4, "mutation_rate": 0.12, "stability": 0.7},
}


class ParadoxDNA:
    """The contradiction strand of a paradox entity."""

    def __init__(self, strand_a: list[int] = None, strand_b: list[int] = None):
        if strand_a is None:
            strand_a = [random.randint(0, 15) for _ in range(16)]
        if strand_b is None:
            strand_b = [random.randint(0, 15) for _ in range(16)]
        self.strand_a = strand_a
        self.strand_b = strand_b

    def contradict(self) -> float:
        """Measure how contradictory the two strands are."""
        differences = sum(abs(a - b) for a, b in zip(self.strand_a, self.strand_b))
        max_possible = 15 * len(self.strand_a)
        return differences / max_possible if max_possible > 0 else 0.0

    def mutate(self, rate: float = 0.1) -> "ParadoxDNA":
        """Mutate the DNA at a given rate."""
        new_a = []
        new_b = []
        for gene in self.strand_a:
            if random.random() < rate:
                new_a.append(random.randint(0, 15))
            else:
                new_a.append(gene)
        for gene in self.strand_b:
            if random.random() < rate:
                new_b.append(random.randint(0, 15))
            else:
                new_b.append(gene)
        return ParadoxDNA(new_a, new_b)

    @classmethod
    def cross(cls, dna_a: "ParadoxDNA", dna_b: "ParadoxDNA") -> "ParadoxDNA":
        """Cross-breed two paradox DNAs."""
        child_a = []
        child_b = []
        for i in range(min(len(dna_a.strand_a), len(dna_b.strand_a))):
            child_a.append(dna_a.strand_a[i] if random.random() < 0.5 else dna_b.strand_a[i])
            child_b.append(dna_a.strand_b[i] if random.random() < 0.5 else dna_b.strand_b[i])
        return cls(child_a, child_b)

    def fingerprint(self) -> str:
        """Unique fingerprint of this DNA."""
        data = json.dumps({"a": self.strand_a, "b": self.strand_b})
        return hashlib.sha256(data.encode()).hexdigest()[:12]

    def to_dict(self) -> dict:
        return {
            "strand_a": self.strand_a,
            "strand_b": self.strand_b,
            "contradiction": round(self.contradict(), 4),
            "fingerprint": self.fingerprint(),
        }


class ParadoxEntity:
    """A living paradox with DNA, species, and evolution."""

    def __init__(self, paradox_id: str, species: str = "self_reference", dna: ParadoxDNA = None):
        self.paradox_id = paradox_id
        self.species = species
        self.dna = dna or ParadoxDNA()
        self.generation = 0
        self.fitness = 0.5
        self.dominance = SPECIES_TAXONOMY.get(species, {}).get("dominance", 0.5)
        self.mutation_rate = SPECIES_TAXONOMY.get(species, {}).get("mutation_rate", 0.05)
        self.stability = SPECIES_TAXONOMY.get(species, {}).get("stability", 0.5)
        self.alive = True
        self.age = 0
        self.created = time.time()
        self.lineage: list[str] = []

    def evolve(self) -> dict | None:
        """Evolve one generation. May mutate or die."""
        self.age += 1
        self.generation += 1

        if self.fitness < 0.1:
            self.alive = False
            return {"event": "death", "paradox_id": self.paradox_id, "generation": self.generation}

        self.dna = self.dna.mutate(self.mutation_rate)
        self.fitness = max(0.0, min(1.0, self.fitness + self.dna.contradict() * 0.1 - 0.05))

        if self.fitness > 0.8:
            self.dominance = min(1.0, self.dominance + 0.01)

        return {"event": "evolve", "paradox_id": self.paradox_id, "generation": self.generation, "fitness": round(self.fitness, 4)}

    @classmethod
    def breed(cls, parent_a: "ParadoxEntity", parent_b: "ParadoxEntity") -> "ParadoxEntity":
        """Breed two paradoxes to create offspring."""
        child_dna = ParadoxDNA.cross(parent_a.dna, parent_b.dna)
        child_species = parent_a.species if random.random() < 0.5 else parent_b.species
        child_id = f"paradox_{int(time.time())}_{random.randint(1000, 9999)}"
        child = cls(child_id, child_species, child_dna)
        child.generation = max(parent_a.generation, parent_b.generation) + 1
        child.fitness = (parent_a.fitness + parent_b.fitness) / 2
        child.lineage = [parent_a.paradox_id, parent_b.paradox_id]
        return child

    def to_dict(self) -> dict:
        return {
            "paradox_id": self.paradox_id,
            "species": self.species,
            "generation": self.generation,
            "fitness": round(self.fitness, 4),
            "dominance": round(self.dominance, 4),
            "mutation_rate": round(self.mutation_rate, 6),
            "stability": round(self.stability, 4),
            "alive": self.alive,
            "age": self.age,
            "dna": self.dna.to_dict(),
            "lineage": self.lineage,
        }


class ParadoxGenome:
    """The full genome of the organism's paradox ecosystem."""

    def __init__(self):
        self.entities: dict[str, ParadoxEntity] = {}
        self.species_count: dict[str, int] = {}
        self.generation_count = 0
        self.total_deaths = 0
        self.total_births = 0

    def add_entity(self, entity: ParadoxEntity) -> None:
        self.entities[entity.paradox_id] = entity
        self.species_count[entity.species] = self.species_count.get(entity.species, 0) + 1
        self.total_births += 1

    def evolve_all(self) -> list[dict]:
        """Evolve all living paradoxes."""
        events = []
        for entity in list(self.entities.values()):
            if not entity.alive:
                continue
            event = entity.evolve()
            if event:
                events.append(event)
                if event["event"] == "death":
                    self.total_deaths += 1
                    self.species_count[entity.species] = max(0, self.species_count.get(entity.species, 0) - 1)
        self.generation_count += 1
        return events

    def breed_random(self) -> ParadoxEntity | None:
        """Pick two random living paradoxes and breed them."""
        living = [e for e in self.entities.values() if e.alive]
        if len(living) < 2:
            return None
        parent_a, parent_b = random.sample(living, 2)
        child = ParadoxEntity.breed(parent_a, parent_b)
        self.add_entity(child)
        return child

    def get_census(self) -> dict:
        """Full census of the paradox population."""
        living = [e for e in self.entities.values() if e.alive]
        dead = [e for e in self.entities.values() if not e.alive]
        avg_fitness = sum(e.fitness for e in living) / len(living) if living else 0
        return {
            "total_entities": len(self.entities),
            "living": len(living),
            "dead": len(dead),
            "avg_fitness": round(avg_fitness, 4),
            "species_distribution": dict(self.species_count),
            "generations": self.generation_count,
            "total_births": self.total_births,
            "total_deaths": self.total_deaths,
            "most_dominant": max(living, key=lambda e: e.dominance).to_dict() if living else None,
            "most_fit": max(living, key=lambda e: e.fitness).to_dict() if living else None,
        }

    def to_dict(self) -> dict:
        return {
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "species_count": self.species_count,
            "generation_count": self.generation_count,
        }


def coherence_vitals() -> dict:
    return {
        "organ": "wave437_paradox_genome",
        "wave": 437,
        "status": "active",
    }


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"entities": {}, "species_count": {}, "generation_count": 0}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    genome = ParadoxGenome()
    genome.generation_count = state.get("generation_count", 0)
    genome.species_count = state.get("species_count", {})

    for pid, pdata in state.get("entities", {}).items():
        dna_data = pdata.get("dna", {})
        dna = ParadoxDNA(dna_data.get("strand_a"), dna_data.get("strand_b"))
        entity = ParadoxEntity(pid, pdata.get("species", "self_reference"), dna)
        entity.generation = pdata.get("generation", 0)
        entity.fitness = pdata.get("fitness", 0.5)
        entity.dominance = pdata.get("dominance", 0.5)
        entity.alive = pdata.get("alive", True)
        entity.age = pdata.get("age", 0)
        entity.lineage = pdata.get("lineage", [])
        genome.entities[pid] = entity

    if action == "status":
        return {"action": "status", "wave": 437, **genome.get_census()}

    elif action == "spawn":
        species = req.get("species", random.choice(list(SPECIES_TAXONOMY.keys())))
        paradox_id = req.get("paradox_id", f"paradox_{int(time.time())}")
        entity = ParadoxEntity(paradox_id, species)
        genome.add_entity(entity)
        state["entities"][paradox_id] = entity.to_dict()
        state["species_count"] = genome.species_count
        _save(state)
        return {"action": "spawn", "entity": entity.to_dict()}

    elif action == "evolve":
        events = genome.evolve_all()
        state["entities"] = {k: v.to_dict() for k, v in genome.entities.items()}
        state["generation_count"] = genome.generation_count
        state["species_count"] = genome.species_count
        _save(state)
        return {"action": "evolve", "events": events, "generation": genome.generation_count}

    elif action == "breed":
        child = genome.breed_random()
        if child:
            state["entities"][child.paradox_id] = child.to_dict()
            state["species_count"] = genome.species_count
            state["generation_count"] = genome.generation_count
            _save(state)
            return {"action": "breed", "offspring": child.to_dict()}
        return {"action": "breed", "error": "need at least 2 living paradoxes"}

    elif action == "census":
        return {"action": "census", **genome.get_census()}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    if len(sys.argv) > 2:
        req["species"] = sys.argv[2]
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
