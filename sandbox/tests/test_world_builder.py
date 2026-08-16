import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from world_builder import World  # noqa: E402


class WorldBuilderTests(unittest.TestCase):
    def setUp(self):
        self.world = World(timeout=5)

    def test_compiles_accepts_valid_syntax(self):
        self.assertTrue(World.compiles("def f():\n    return 1\n"))

    def test_compiles_rejects_invalid_syntax(self):
        self.assertFalse(World.compiles("def f(:\n    return 1\n"))

    def test_run_harness_reports_full_pass(self):
        candidate = "def add(a, b):\n    return a + b\n"
        harness = (
            "import json\n"
            "import candidate\n"
            "CASES = [((1, 2), 3), ((0, 0), 0)]\n"
            "passed = sum(1 for args, expected in CASES if candidate.add(*args) == expected)\n"
            "print('SANDBOX_RESULT_JSON=' + json.dumps({'passed': passed, 'total': len(CASES)}))\n"
        )
        result = self.world.run_harness(candidate, harness)
        self.assertTrue(result.success)
        self.assertTrue(result.solved)
        self.assertEqual(result.fitness, 1.0)

    def test_run_harness_reports_partial_pass_and_not_solved(self):
        candidate = "def add(a, b):\n    return a - b\n"
        harness = (
            "import json\n"
            "import candidate\n"
            "CASES = [((1, 2), 3), ((5, 0), 5)]\n"
            "passed = sum(1 for args, expected in CASES if candidate.add(*args) == expected)\n"
            "print('SANDBOX_RESULT_JSON=' + json.dumps({'passed': passed, 'total': len(CASES)}))\n"
        )
        result = self.world.run_harness(candidate, harness)
        self.assertTrue(result.success)
        self.assertFalse(result.solved)
        self.assertEqual(result.fitness, 0.5)

    def test_syntax_error_candidate_yields_zero_fitness_and_failure(self):
        candidate = "def add(a, b)\n    return a + b\n"  # missing colon
        harness = (
            "import json\n"
            "try:\n"
            "    import candidate\n"
            "    print('SANDBOX_RESULT_JSON=' + json.dumps({'passed': 0, 'total': 1}))\n"
            "except Exception as exc:\n"
            "    print('SANDBOX_RESULT_JSON=' + json.dumps({'passed': 0, 'total': 1, 'error': repr(exc)}))\n"
        )
        result = self.world.run_harness(candidate, harness)
        self.assertFalse(result.solved)
        self.assertEqual(result.fitness, 0.0)

    def test_infinite_loop_is_stopped_and_never_reported_as_success(self):
        # An infinite loop must never be allowed to "succeed": it is stopped
        # either by the wall-clock timeout (timed_out=True) or, on POSIX, by
        # the CPU rlimit killing the process first (a nonzero/None exit
        # code). Either outcome is acceptable; silently running forever or
        # reporting success is not.
        world = World(timeout=2, cpu_seconds=1)
        candidate = "while True:\n    pass\n"
        result = world.run_code(candidate)
        self.assertFalse(result.success)
        self.assertTrue(result.timed_out or result.exit_code != 0)

    def test_restricted_environment_hides_secrets(self):
        candidate = (
            "import json, os\n"
            "print('SANDBOX_RESULT_JSON=' + json.dumps({'has_secret': 'SUPER_SECRET' in os.environ}))\n"
        )
        with patch.dict(os.environ, {"SUPER_SECRET": "do-not-leak"}):
            result = self.world.run_code(candidate)
        self.assertIn('"has_secret": false', result.stdout)


if __name__ == "__main__":
    unittest.main()
