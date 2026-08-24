import concurrent.futures
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

from lab.runtime_vault import (
    append_jsonl,
    ledger_path,
    path,
    read_json,
    read_jsonl,
    root,
    state_path,
    write_json,
)


class TestRuntimeVault:
    def test_environment_overrides_root_and_rejects_escape(self, tmp_path, monkeypatch):
        monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
        assert root() == tmp_path.resolve()
        assert state_path("pulse.json") == tmp_path / "state" / "pulse.json"
        assert ledger_path("proof.jsonl") == tmp_path / "ledgers" / "proof.jsonl"
        try:
            path("..", "escape")
        except ValueError:
            pass
        else:
            raise AssertionError("vault path escaped")

    def test_json_writes_are_atomic_and_complete(self, tmp_path):
        target = tmp_path / "nested" / "state.json"
        payload = {"ritual": "pulse", "beats": 2}
        write_json(target, payload)
        assert read_json(target) == payload
        assert list(target.parent.glob(".state.json.*")) == []

    def test_concurrent_appends_do_not_interleave(self, tmp_path):
        ledger = tmp_path / "proof.jsonl"

        def append_batch(worker):
            return [append_jsonl(ledger, {"worker": worker, "item": item}) for item in range(5)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(append_batch, range(8)))
        records = read_jsonl(ledger)
        assert len(records) == 40
        assert len({json.dumps(record, sort_keys=True) for record in records}) == 40

    def test_corrupt_lines_are_quarantined_from_reads(self, tmp_path):
        ledger = tmp_path / "ledger.jsonl"
        ledger.write_text('{"type":"good"}\nnot-json\n\n{"type":"also-good"}\n', encoding="utf-8")
        assert [record["type"] for record in read_jsonl(ledger)] == ["good", "also-good"]

    def test_pulse_state_defaults_to_runtime_vault(self, tmp_path, monkeypatch):
        monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
        import importlib.util

        path = ROOT / "lab" / "chrono_forge" / "0_primal_core" / "pulse_driver.py"
        spec = importlib.util.spec_from_file_location("vault_pulse_driver", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        expected = tmp_path / "state" / "pulse" / "state.json"
        assert module.STATE == expected
        module.pulse(1)
        assert read_json(expected)["beats"] == 1

    def test_pinned_outputs_default_to_repository_vault(self):
        import lab.run_pinned as runner
        vault_root = ROOT / ".runtime" / "lab"
        assert runner.REPORT == vault_root / "reports" / "pinned-report.json"
        assert runner.LEDGER == vault_root / "ledgers" / "proof.jsonl"
