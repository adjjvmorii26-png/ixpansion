"""Tests for Wave 437 — Paradox Genome."""
import pytest
from api.wave437_paradox_genome import (
    ParadoxDNA, ParadoxEntity, ParadoxGenome, handler, coherence_vitals, SPECIES_TAXONOMY
)

def test_coherence_vitals():
    v = coherence_vitals()
    assert v["organ"] == "wave437_paradox_genome"
    assert v["wave"] == 437

def test_paradox_dna_init():
    dna = ParadoxDNA()
    assert len(dna.strand_a) == 16
    assert len(dna.strand_b) == 16

def test_paradox_dna_contradict():
    dna = ParadoxDNA([0]*16, [15]*16)
    assert dna.contradict() == 1.0
    dna2 = ParadoxDNA([5]*16, [5]*16)
    assert dna2.contradict() == 0.0

def test_paradox_dna_mutate():
    dna = ParadoxDNA()
    original = dna.fingerprint()
    mutated = dna.mutate(1.0)
    assert mutated.fingerprint() != original

def test_paradox_dna_cross():
    dna_a = ParadoxDNA()
    dna_b = ParadoxDNA()
    child = ParadoxDNA.cross(dna_a, dna_b)
    assert len(child.strand_a) == 16

def test_paradox_dna_fingerprint():
    dna = ParadoxDNA()
    fp = dna.fingerprint()
    assert len(fp) == 12

def test_paradox_entity_init():
    e = ParadoxEntity("p1", "self_reference")
    assert e.paradox_id == "p1"
    assert e.species == "self_reference"
    assert e.alive is True
    assert e.generation == 0

def test_paradox_entity_evolve():
    e = ParadoxEntity("p2", "temporal_loop")
    e.fitness = 0.8
    event = e.evolve()
    assert event["event"] == "evolve"
    assert e.generation == 1

def test_paradox_entity_breed():
    a = ParadoxEntity("pa", "causal_cycle")
    b = ParadoxEntity("pb", "identity_split")
    child = ParadoxEntity.breed(a, b)
    assert child.generation == 1
    assert child.species in ["causal_cycle", "identity_split"]

def test_paradox_genome_init():
    g = ParadoxGenome()
    assert g.total_births == 0

def test_paradox_genome_add():
    g = ParadoxGenome()
    e = ParadoxEntity("p1", "entropy_inversion")
    g.add_entity(e)
    assert g.total_births == 1
    assert "entropy_inversion" in g.species_count

def test_paradox_genome_evolve():
    g = ParadoxGenome()
    for i in range(3):
        e = ParadoxEntity(f"p{i}", "quantum_duality")
        e.fitness = 0.8
        g.add_entity(e)
    events = g.evolve_all()
    assert len(events) == 3
    assert g.generation_count == 1

def test_paradox_genome_breed():
    g = ParadoxGenome()
    a = ParadoxEntity("pa", "fractal_recurse")
    b = ParadoxEntity("pb", "emergent_whole")
    g.add_entity(a)
    g.add_entity(b)
    child = g.breed_random()
    assert child is not None
    assert child.paradox_id in g.entities

def test_paradox_genome_census():
    g = ParadoxGenome()
    e = ParadoxEntity("p1", "self_reference")
    g.add_entity(e)
    census = g.get_census()
    assert census["living"] == 1
    assert census["total_entities"] == 1

def test_handler_status():
    result = handler({"action": "status"})
    assert result["action"] == "status"
    assert result["wave"] == 437

def test_handler_spawn():
    result = handler({"action": "spawn", "paradox_id": "test_p", "species": "self_reference"})
    assert result["action"] == "spawn"
    assert result["entity"]["paradox_id"] == "test_p"

def test_handler_evolve():
    handler({"action": "spawn", "paradox_id": "e1", "species": "temporal_loop"})
    result = handler({"action": "evolve"})
    assert result["action"] == "evolve"
    assert "events" in result

def test_handler_breed():
    handler({"action": "spawn", "paradox_id": "b1", "species": "causal_cycle"})
    handler({"action": "spawn", "paradox_id": "b2", "species": "identity_split"})
    result = handler({"action": "breed"})
    assert result["action"] == "breed"

def test_handler_census():
    result = handler({"action": "census"})
    assert result["action"] == "census"
    assert "living" in result

def test_handler_unknown():
    result = handler({"action": "unknown"})
    assert "error" in result

def test_species_taxonomy():
    assert len(SPECIES_TAXONOMY) == 8
    assert all("dominance" in v for v in SPECIES_TAXONOMY.values())

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
