import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sandbox_engine import Genome, SandboxEngine  # noqa: E402


class SandboxEngineTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.genome_path = Path(self.tmpdir.name) / "genome.json"

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_tick_records_progress_and_persists(self):
        engine = SandboxEngine(genome=Genome(self.genome_path), verbose=False)
        engine.run(3)
        self.assertTrue(self.genome_path.exists())
        self.assertEqual(engine.genome.tick_count, 3)
        self.assertEqual(len(engine.genome.history), 3)

    def test_state_survives_reload(self):
        engine = SandboxEngine(genome=Genome(self.genome_path), verbose=False)
        engine.run(2)
        reloaded = Genome(self.genome_path)
        self.assertEqual(reloaded.tick_count, 2)
        self.assertEqual(len(reloaded.records), len(engine.genome.records))

    def test_eventually_solves_all_builtin_challenges(self):
        engine = SandboxEngine(genome=Genome(self.genome_path), verbose=False)
        engine.run(40)
        status = engine.status()
        self.assertEqual(status["challenges_solved"], status["challenges_known"])


if __name__ == "__main__":
    unittest.main()
