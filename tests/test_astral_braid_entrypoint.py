"""Regression coverage for the Astral Braid module CLI entrypoint."""
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_module_cli_writes_a_certified_braid_report(tmp_path):
    report_path = tmp_path / "astral-braid.json"
    transcript_path = tmp_path / "astral-bus.jsonl"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "bridges.astral_braid",
            "--seed",
            "1337",
            "--steps",
            "6",
            "--sites",
            "5",
            "--transcript",
            str(transcript_path),
            "--output",
            str(report_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["experiment"] == "astral-braid-conservatory"
    assert report["source_dream_id"]
    assert report["source_evidence_hash"]
    assert report["certificate_hash"]
    assert len(report["candidates"]) == 3
    assert transcript_path.is_file()
