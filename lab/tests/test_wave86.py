from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

class TestCodeFossilRecord:
    def test_demo(self):
        from lab.experiments.code_fossil_record import demo
        r = demo(); assert r["record"] == "code_fossil_record"; assert r["fossils_found"] >= 0

class TestMutationTesting:
    def test_demo(self):
        from lab.experiments.mutation_testing import demo
        r = demo(); assert r["testing"] == "mutation_testing"; assert r["files_tested"] > 0

class TestParallelUniverse:
    def test_demo(self):
        from lab.experiments.parallel_universe import demo
        r = demo(); assert r["simulation"]["universes"] == 5; assert r["simulation"]["ticks"] == 20

class TestDreamNetwork:
    def test_demo(self):
        from lab.experiments.dream_network import demo
        r = demo(); assert r["dreams"] == 12; assert r["themes"]["flying"] >= 1

class TestRealityDistortionField:
    def test_demo(self):
        from lab.experiments.reality_distortion_field import demo
        r = demo(); assert r["sources"] == 3; assert r["measurements"] == 10

class TestTemporalLoopDetector:
    def test_demo(self):
        from lab.experiments.temporal_loop_detector import demo
        r = demo(); assert r["modules"] > 0
