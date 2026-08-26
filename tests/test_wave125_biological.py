"""Wave 125 -- Biological Architecture Layer tests."""
from __future__ import annotations

from api.code_organism import CodeOrganism, OrganismEcosystem
from api.digital_metabolism import DigitalMetabolism, MetabolicPathway
from api.digital_immune_system import DigitalImmuneSystem, ImmuneResponse
from api.neural_vine import NeuralVine, NeuralVineNetwork
from api.synaptic_spring import SynapticSpring, Synapse
from api.genetic_code_engine import GeneticCodeEngine, Genome
from api.cellular_automaton import CellularAutomaton
from api.evolutionary_pressure import EvolutionaryPressureEngine, PressureEvent


class TestCodeOrganism:
    def test_birth_and_metabolise(self):
        org = CodeOrganism("alpha")
        energy = org.metabolise(10.0)
        assert energy > 0
        assert org.is_alive()

    def test_reproduce(self):
        org = CodeOrganism("parent")
        child = org.reproduce("child")
        assert child.generation == 1
        assert len(org.offspring) == 1

    def test_organism_ecosystem(self):
        eco = OrganismEcosystem()
        eco.birth("a")
        eco.birth("b")
        census = eco.census()
        assert census["total"] == 2
        assert census["alive"] == 2


class TestDigitalMetabolism:
    def test_create_and_process(self):
        dm = DigitalMetabolism()
        dm.create_pathway("glycolysis", efficiency=0.6)
        result = dm.metabolise("glycolysis", 100.0)
        assert result["useful_output"] > 0
        assert result["energy"] > 0

    def test_energy_balance(self):
        dm = DigitalMetabolism()
        dm.create_pathway("p1")
        dm.metabolise("p1", 50.0)
        bal = dm.energy_balance()
        assert bal["pool"] > 100.0

    def test_status(self):
        dm = DigitalMetabolism()
        dm.create_pathway("p")
        s = dm.status()
        assert s["pathways"] == 1


class TestDigitalImmuneSystem:
    def test_detect_and_neutralise(self):
        immune = DigitalImmuneSystem()
        result = immune.detect("virus", 0.8)
        assert result["detected"] is True
        assert immune.check_memory("virus") == 1

    def test_below_threshold(self):
        immune = DigitalImmuneSystem()
        result = immune.detect("minor", 0.1)
        assert result["detected"] is False

    def test_status(self):
        immune = DigitalImmuneSystem()
        immune.detect("t", 0.9)
        s = immune.status()
        assert s["total_responses"] == 1


class TestNeuralVine:
    def test_grow(self):
        vine = NeuralVine("ivy")
        seg = vine.grow_toward("up", data_density=0.8)
        assert seg.length > 0
        assert len(vine.segments) == 1

    def test_network(self):
        net = NeuralVineNetwork()
        net.plant("v1")
        net.plant("v2")
        grown = net.grow_cycle()
        assert grown == 2

    def test_status(self):
        net = NeuralVineNetwork()
        net.plant("v1")
        s = net.status()
        assert s["total_vines"] == 1


class TestSynapticSpring:
    def test_connect_and_stimulate(self):
        ss = SynapticSpring()
        ss.connect("A", "B", 0.3)
        results = ss.stimulate("A")
        assert len(results) == 1
        assert results[0]["strength"] > 0.3

    def test_decay(self):
        ss = SynapticSpring()
        syn = ss.connect("X", "Y", 0.8)
        weakened = ss.global_decay()
        assert weakened >= 1
        assert syn.strength < 0.8

    def test_status(self):
        ss = SynapticSpring()
        ss.connect("A", "B")
        s = ss.status()
        assert s["total_synapses"] == 1


class TestGeneticCodeEngine:
    def test_seed_and_evolve(self):
        gce = GeneticCodeEngine()
        g1 = gce.seed("ACGTACGT", "parent1")
        g2 = gce.seed("TTTTCCCC", "parent2")
        gce.evaluate_fitness(g1)
        gce.evaluate_fitness(g2)
        child = gce.evolve(g1, g2)
        assert child.generation == 1

    def test_select_fittest(self):
        gce = GeneticCodeEngine()
        g1 = gce.seed("AAAA")
        g2 = gce.seed("GGGG")
        gce.evaluate_fitness(g1)
        gce.evaluate_fitness(g2)
        fittest = gce.select_fittest(1)
        assert len(fittest) == 1

    def test_status(self):
        gce = GeneticCodeEngine()
        gce.seed("ACGT")
        s = gce.status()
        assert s["population"] == 1


class TestCellularAutomaton:
    def test_glider(self):
        ca = CellularAutomaton(10, 10)
        ca.set_alive(1, 0)
        ca.set_alive(2, 1)
        ca.set_alive(0, 2)
        ca.set_alive(1, 2)
        ca.set_alive(2, 2)
        assert ca.population() == 5
        ca.step()
        assert ca.status()["generation"] == 1

    def test_run(self):
        ca = CellularAutomaton(10, 10)
        ca.set_alive(5, 5)
        history = ca.run(5)
        assert len(history) == 5

    def test_status(self):
        ca = CellularAutomaton(10, 10)
        s = ca.status()
        assert s["population"] == 0


class TestEvolutionaryPressure:
    def test_apply_pressure(self):
        ep = EvolutionaryPressureEngine()
        event = ep.apply_pressure("famine", 0.9, duration=3)
        assert event.active is True

    def test_tick(self):
        ep = EvolutionaryPressureEngine()
        ep.apply_pressure("flood", 0.8, duration=2)
        ep.tick()
        results = ep.tick()
        assert len(results) == 1
        assert results[0]["active"] is False

    def test_status(self):
        ep = EvolutionaryPressureEngine()
        ep.apply_pressure("drought", 0.5)
        s = ep.status()
        assert s["total_pressures"] == 1
