"""Tests for the runtime-neutral Live Test Chamber."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "skills" / "live-reusable-test-surface" / "scripts" / "live_test_chamber.py"


class LiveTestChamberTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "ok.py").write_text('print("chamber-ready")\n', encoding="utf-8")
        (self.root / "bad.py").write_text('raise SystemExit(7)\n', encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def run_chamber(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root), *args],
            text=True, capture_output=True, timeout=10, check=False,
        )

    def test_python_target_passes_explicit_assertions(self):
        result = self.run_chamber(
            "--runtime", "python", "--target", "ok.py",
            "--expect-exit", "0", "--expect-stdout", "chamber-ready",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["assertions"], [
            {"kind": "exit_code", "expected": 0, "actual": 0, "passed": True},
            {"kind": "stdout_contains", "expected": "chamber-ready", "passed": True},
        ])

    def test_nonzero_exit_fails(self):
        result = self.run_chamber(
            "--runtime", "python", "--target", "bad.py", "--expect-exit", "0",
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["result"], "FAIL")

    def test_path_escape_is_blocked(self):
        result = self.run_chamber(
            "--runtime", "python", "--target", "../outside.py", "--expect-exit", "0",
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["result"], "BLOCKED")

    def test_timeout_is_a_failure(self):
        (self.root / "slow.py").write_text("import time; time.sleep(2)\n", encoding="utf-8")
        result = self.run_chamber(
            "--runtime", "python", "--target", "slow.py",
            "--expect-exit", "0", "--timeout", "0.2",
        )
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertTrue(report["timed_out"])
        self.assertEqual(report["result"], "FAIL")

    def test_timeout_kills_child_processes(self):
        import os
        if os.name == "nt":
            self.skipTest("Process-group descendant behavior is platform-specific")
        (self.root / "parent.py").write_text(
            "import subprocess, sys, time\\n"
            "subprocess.Popen([sys.executable, '-c', "
            "'import time; time.sleep(0.6); open(\\\"child-survived\\\", \\\"w\\\").write(\\\"yes\\\")'])\\n"
            "time.sleep(5)\\n",
            encoding="utf-8",
        )
        result = self.run_chamber(
            "--runtime", "python", "--target", "parent.py",
            "--expect-exit", "0", "--timeout", "0.2",
        )
        self.assertEqual(result.returncode, 1)
        import time
        time.sleep(0.8)
        self.assertFalse((self.root / "child-survived").exists())

    def test_report_is_persisted_inside_root(self):
        result = self.run_chamber(
            "--runtime", "python", "--target", "ok.py", "--expect-exit", "0",
            "--report", "artifacts/report.json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        saved = json.loads((self.root / "artifacts/report.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["result"], "PASS")
        self.assertEqual(saved["report_path"], "artifacts/report.json")
        stdout_report = json.loads(result.stdout)
        self.assertEqual(stdout_report["report_path"], saved["report_path"])

    def test_large_stdout_and_stderr_are_bounded(self):
        (self.root / "large.py").write_text(
            'import sys; print("x" * 100000); print("y" * 100000, file=sys.stderr)\n',
            encoding="utf-8",
        )
        result = self.run_chamber(
            "--runtime", "python", "--target", "large.py", "--expect-exit", "0",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["result"], "PASS")
        for stream in ("stdout", "stderr"):
            self.assertIn("output truncated at 65536 bytes", report[stream])
            self.assertLessEqual(len(report[stream].encode("utf-8")), 65600)

    def test_report_cannot_overwrite_target(self):
        original = (self.root / "ok.py").read_text(encoding="utf-8")
        result = self.run_chamber(
            "--runtime", "python", "--target", "ok.py", "--expect-exit", "0",
            "--report", "ok.py",
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["result"], "BLOCKED")
        self.assertEqual((self.root / "ok.py").read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
