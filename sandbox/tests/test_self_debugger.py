import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from idea_lab import IdeaLab  # noqa: E402
from self_debugger import SelfDebugger  # noqa: E402
from world_builder import World  # noqa: E402


class SelfDebuggerTests(unittest.TestCase):
    def setUp(self):
        self.world = World(timeout=5)
        self.lab = IdeaLab(rng=random.Random(7))
        self.debugger = SelfDebugger(
            self.world, self.lab, rng=random.Random(7), max_generations=40, population_size=10
        )

    def test_heals_every_builtin_buggy_seed(self):
        for name in self.lab.list_challenges():
            challenge = self.lab.challenge_by_name(name)
            report = self.debugger.heal(challenge.buggy_seed, challenge.harness)
            self.assertTrue(report.healed, f"{name} should be healed")
            self.assertTrue(report.best_result.solved, f"{name} should reach full fitness")

    def test_already_passing_code_is_reported_healed_with_no_strategy(self):
        challenge = self.lab.challenge_by_name("clamp")
        report = self.debugger.heal(challenge.reference_solution, challenge.harness)
        self.assertTrue(report.healed)
        self.assertIsNone(report.strategy_used)
        self.assertEqual(len(report.attempts), 0)

    def test_llm_repair_is_skipped_when_bridge_unavailable(self):
        from llm_bridge import LLMBridge

        debugger = SelfDebugger(self.world, self.lab, llm=LLMBridge(api_key="", base_url=""))
        challenge = self.lab.challenge_by_name("binary_search")
        result = debugger._run_llm_repair(challenge.buggy_seed, self.world.run_harness(
            challenge.buggy_seed, challenge.harness
        ), challenge.harness, [])
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
