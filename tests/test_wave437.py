"""Tests for Wave 437: Paradox Genome."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave437_paradox_genome as m
def test_vitals():
    assert m.coherence_vitals()["wave"] == 437
def test_spawn_breed():
    assert m.handler({"action": "spawn", "name": "liar"})["status"] == "spawned"
    assert m.handler({"action": "spawn", "name": "truth"})["status"] == "spawned"
    r = m.handler({"action": "breed"})
    assert r["status"] == "bred" and "dna" in r["child"]
