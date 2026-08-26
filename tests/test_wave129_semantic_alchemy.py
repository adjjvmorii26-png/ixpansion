"""Wave 129 -- Semantic Alchemy Layer tests."""
from __future__ import annotations

from api.semantic_transmuter import SemanticTransmuter, Transmutation
from api.conceptual_alchemist import ConceptualAlchemist, Concept
from api.metaphor_engine import MetaphorEngine, Metaphor
from api.semantic_catalyst import SemanticCatalyst, CatalystReaction
from api.ontological_forge import OntologicalForge, OntologicalClass
from api.meaning_furnace import MeaningFurnace, MeaningExtract
from api.hermeneutic_engine import HermeneuticEngine, Interpretation
from api.semantic_precipitate import SemanticPrecipitate, Crystal


class TestSemanticTransmuter:
    def test_transmute_and_complete(self):
        st = SemanticTransmuter()
        t = st.transmute("joy", "emotion", "color")
        result = st.complete_transmutation(t.id, "golden yellow", 0.85)
        assert result["fidelity"] == 0.85

    def test_domain_coverage(self):
        st = SemanticTransmuter()
        st.transmute("x", "A", "B")
        st.transmute("y", "A", "B")
        coverage = st.domain_coverage()
        assert "A->B" in coverage

    def test_status(self):
        st = SemanticTransmuter()
        s = st.status()
        assert s["total_transmutations"] == 0


class TestConceptualAlchemist:
    def test_transmute_and_refine(self):
        ca = ConceptualAlchemist()
        c = ca.transmute("gravity", "force between masses")
        purity = ca.refine(c.id, "Spacetime curvature")
        assert purity > 0.1

    def test_philosopher_stone(self):
        ca = ConceptualAlchemist()
        c = ca.transmute("c1", "raw")
        ca.refine(c.id, "insight1")
        stone = ca.philosopher_stone()
        assert stone["name"] == "c1"

    def test_status(self):
        ca = ConceptualAlchemist()
        ca.transmute("c", "raw")
        s = ca.status()
        assert s["total_concepts"] == 1


class TestMetaphorEngine:
    def test_create_and_map(self):
        me = MetaphorEngine()
        m = me.create("brain", "computer")
        me.add_mapping(m.id, "neurons", "processors")
        me.add_mapping(m.id, "synapses", "connections")
        assert m.strength > 0

    def test_strongest(self):
        me = MetaphorEngine()
        m1 = me.create("a", "b")
        me.add_mapping(m1.id, "x", "y")
        strongest = me.strongest_metaphor()
        assert strongest["source"] == "a"

    def test_status(self):
        me = MetaphorEngine()
        me.create("a", "b")
        s = me.status()
        assert s["total_metaphors"] == 1


class TestSemanticCatalyst:
    def test_catalyse(self):
        sc = SemanticCatalyst("fast_catalyst")
        reaction = sc.catalyse("raw data")
        result = sc.complete_reaction(reaction, "refined data", 3.0)
        assert result["speedup"] == 3.0

    def test_avg_speedup(self):
        sc = SemanticCatalyst("cat")
        r = sc.catalyse("d1")
        sc.complete_reaction(r, "o1", 2.0)
        assert sc.avg_speedup() == 2.0

    def test_status(self):
        sc = SemanticCatalyst("test")
        s = sc.status()
        assert s["name"] == "test"


class TestOntologicalForge:
    def test_forge(self):
        of = OntologicalForge()
        cls = of.forge("SentientEntity")
        of.add_property(cls.id, "self_awareness")
        result = of.get_class(cls.id)
        assert "self_awareness" in result["properties"]

    def test_ontology_tree(self):
        of = OntologicalForge()
        of.forge("A")
        of.forge("B", parent="A")
        tree = of.ontology_tree()
        assert len(tree) == 2

    def test_status(self):
        of = OntologicalForge()
        of.forge("X")
        s = of.status()
        assert s["total_classes"] == 1


class TestMeaningFurnace:
    def test_burn(self):
        mf = MeaningFurnace(temperature=200.0)
        extract = mf.burn("noisy raw data stream")
        assert extract.noise_removed > 0
        assert extract.pure_meaning != ""

    def test_temperature_up(self):
        mf = MeaningFurnace(100.0)
        new_temp = mf.temperature_up(50.0)
        assert new_temp == 150.0

    def test_status(self):
        mf = MeaningFurnace()
        s = mf.status()
        assert s["temperature"] == 100.0


class TestHermeneuticEngine:
    def test_interpret_and_deepen(self):
        he = HermeneuticEngine()
        interp = he.interpret("the code speaks", "structural")
        depth = he.deepen(interp.id, "layer 1: surface syntax")
        assert depth == 1
        depth = he.deepen(interp.id, "layer 2: hidden intent")
        assert depth == 2

    def test_deepest(self):
        he = HermeneuticEngine()
        i1 = he.interpret("text1")
        i2 = he.interpret("text2")
        he.deepen(i1.id, "l1")
        he.deepen(i1.id, "l2")
        he.deepen(i2.id, "l1")
        deepest = he.deepest_interpretation()
        assert deepest["depth"] == 2

    def test_status(self):
        he = HermeneuticEngine()
        he.interpret("x")
        s = he.status()
        assert s["total_interpretations"] == 1


class TestSemanticPrecipitate:
    def test_precipitate(self):
        sp = SemanticPrecipitate(supersaturation_threshold=0.5)
        result = sp.supersaturate("crystal_a", "meaning solution", 0.8)
        assert result["precipitated"] is True

    def test_below_threshold(self):
        sp = SemanticPrecipitate(supersaturation_threshold=0.9)
        result = sp.supersaturate("weak", "dilute", 0.3)
        assert result["precipitated"] is False

    def test_grow_crystal(self):
        sp = SemanticPrecipitate(supersaturation_threshold=0.5)
        result = sp.supersaturate("c1", "sol", 0.8)
        ok = sp.grow_crystal(result["crystal"]["id"], "facet_1")
        assert ok is True

    def test_status(self):
        sp = SemanticPrecipitate()
        s = sp.status()
        assert s["total_crystals"] == 0
