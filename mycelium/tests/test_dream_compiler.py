import json

from mycelium.cognition.dream_compiler import DreamCompiler, build_demo_network
from mycelium.hyphae.hypha import Spore
from mycelium.interfaces.cli import main


class TestDreamCompiler:
    def test_empty_life_has_no_dream(self):
        network = build_demo_network(seed=3, steps=0)
        assert DreamCompiler().compile(network) is None

    def test_dream_is_reproducible_from_same_history(self):
        first = build_demo_network(seed=11, steps=6)
        second = build_demo_network(seed=11, steps=6)
        left = DreamCompiler().compile(first)
        right = DreamCompiler().compile(second)
        assert left is not None and right is not None
        assert left.payload() == right.payload()

    def test_dream_amplifies_least_expressed_genome_and_becomes_spore(self):
        network = build_demo_network(seed=23, steps=0)
        network.plant(
            Spore("deterministic", {"curiosity": 0.3, "patience": 0.5}, viability=1),
            (0, 0),
        )
        for _ in range(7):
            network.pulse()

        population_size = len(network.hyphae)
        averages = {
            key: sum(hypha.genome.get(key, 0) for hypha in network.hyphae.values()) / population_size
            for key in ("curiosity", "patience")
        }
        weakest = min(averages, key=averages.get)
        experiment = DreamCompiler().compile(network)
        assert experiment is not None
        assert experiment.genome[weakest] > averages[weakest]

        spore = experiment.to_spore()
        assert spore.genome == experiment.genome
        assert spore.spore_id.startswith("dream-")

    def test_cli_simulate_and_dream_emit_json_documents(self, capsys):
        assert main(["simulate", "--seed", "5", "--steps", "2"]) == 0
        simulated = json.loads(capsys.readouterr().out)
        assert simulated["experiment"] == "mycelium-pulse"
        assert simulated["stats"]["journal_events"] > 0

        assert main(["dream", "--seed", "5", "--steps", "3"]) == 0
        dreamed = json.loads(capsys.readouterr().out)
        assert dreamed["dream"]["evidence_hash"]
