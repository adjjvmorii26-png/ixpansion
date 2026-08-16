import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from idea_lab import IdeaLab  # noqa: E402
from world_builder import World  # noqa: E402


class IdeaLabTests(unittest.TestCase):
    def setUp(self):
        self.lab = IdeaLab()
        self.world = World(timeout=5)

    def test_lists_eight_builtin_challenges(self):
        self.assertEqual(len(self.lab.list_challenges()), 8)

    def test_every_reference_solution_passes_its_own_harness(self):
        for name in self.lab.list_challenges():
            challenge = self.lab.challenge_by_name(name)
            result = self.world.run_harness(challenge.reference_solution, challenge.harness)
            self.assertTrue(result.solved, f"{name} reference solution should fully pass")

    def test_every_buggy_seed_fails_its_own_harness(self):
        for name in self.lab.list_challenges():
            challenge = self.lab.challenge_by_name(name)
            result = self.world.run_harness(challenge.buggy_seed, challenge.harness)
            self.assertFalse(result.solved, f"{name} buggy seed should not fully pass")
            self.assertGreater(result.fitness, 0.0, f"{name} buggy seed should partially pass")

    def test_challenge_by_name_unknown_returns_none(self):
        self.assertIsNone(self.lab.challenge_by_name("does-not-exist"))

    def test_propose_challenge_respects_exclude(self):
        names = self.lab.list_challenges()
        excluded = names[:-1]
        challenge = self.lab.propose_challenge(exclude=excluded)
        self.assertEqual(challenge.name, names[-1])

    def test_propose_challenge_falls_back_when_all_excluded(self):
        challenge = self.lab.propose_challenge(exclude=self.lab.list_challenges())
        self.assertIn(challenge.name, self.lab.list_challenges())

    def test_mutate_always_returns_compiling_code(self):
        code = "def clamp(value, low, high):\n    if value < low:\n        return value\n    return value\n"
        for _ in range(20):
            mutant = self.lab.mutate(code)
            self.assertTrue(World.compiles(mutant))

    def test_crossover_returns_compiling_code(self):
        a = "def f(x):\n    if x > 0:\n        return 1\n    return 0\n"
        b = "def f(x):\n    if x >= 0:\n        return 2\n    return -1\n"
        child = self.lab.crossover(a, b)
        self.assertTrue(World.compiles(child))


if __name__ == "__main__":
    unittest.main()
