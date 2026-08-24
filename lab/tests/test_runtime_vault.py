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
    verify_jsonl,
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


class TestLedgerChain:
    def test_concurrent_appends_form_one_valid_chain(self, tmp_path):
        ledger = tmp_path / "proof.jsonl"

        def append_batch(worker):
            return [append_jsonl(ledger, {"worker": worker, "item": item}) for item in range(5)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(append_batch, range(8)))

        records = read_jsonl(ledger)
        audit = verify_jsonl(ledger)
        assert audit["ok"] is True
        assert audit["chained_records"] == 40
        assert audit["segments"] == 1
        assert [record["sequence"] for record in records] == list(range(1, 41))
        assert records[0]["previous_hash"] == "0" * 64

    def test_legacy_prefix_migrates_to_chained_suffix(self, tmp_path):
        ledger = tmp_path / "legacy.jsonl"
        ledger.write_text('{"type":"old"}\n{"type":"also-old"}\n', encoding="utf-8")
        append_jsonl(ledger, {"type": "new"})
        audit = verify_jsonl(ledger)
        assert audit["ok"] is True
        assert audit["legacy_records"] == 2
        assert audit["chained_records"] == 1
        assert audit["segments"] == 1

    def test_tampered_payload_breaks_audit(self, tmp_path):
        ledger = tmp_path / "tamper.jsonl"
        append_jsonl(ledger, {"type": "original", "value": 1})
        lines = ledger.read_text().splitlines()
        record = json.loads(lines[0])
        record["value"] = 999
        lines[0] = json.dumps(record, sort_keys=True, separators=(",", ":"))
        ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
        audit = verify_jsonl(ledger)
        assert audit["ok"] is False
        assert audit["failure"]["kind"] == "chain_mismatch"
        assert audit["failure"]["hash_valid"] is False

    def test_chain_reset_after_valid_chain_is_rejected(self, tmp_path):
        ledger = tmp_path / "reset.jsonl"
        append_jsonl(ledger, {"type": "valid"})
        forged = {
            "type": "reset", "sequence": 1,
            "previous_hash": "0" * 64,
            "entry_hash": append_jsonl(tmp_path / "helper.jsonl", {"seed": 1})["entry_hash"],
        }
        # A hash computed for another payload must not legitimize this reset.
        forged.pop("entry_hash")
        forged["entry_hash"] = "a" * 64
        with ledger.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(forged, sort_keys=True, separators=(",", ":")) + "\n")
        audit = verify_jsonl(ledger)
        assert audit["ok"] is False
        assert audit["failure"]["kind"] == "chain_mismatch"

    def test_invalid_json_fails_closed(self, tmp_path):
        ledger = tmp_path / "invalid.jsonl"
        ledger.write_text('{"complete":true}\n{"broken":\n', encoding="utf-8")
        audit = verify_jsonl(ledger)
        assert audit["ok"] is False
        assert audit["failure"]["kind"] == "invalid_json"

    def test_vault_cli_verifies_and_replays(self, tmp_path):
        from lab.vault_cli import main

        ledger = tmp_path / "cli.jsonl"
        assert main(["replay", "--ledger", str(ledger), "--depth", "5"]) == 0
        append_jsonl(ledger, {"type": "cli-proof"})
        assert main(["verify", "--ledger", str(ledger)]) == 0

    def test_sentinel_fails_closed_on_broken_ledger(self, tmp_path, monkeypatch):
        monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
        import importlib.util

        path = ROOT / "lab" / "chrono_forge" / "2_agents" / "sentinel.py"
        spec = importlib.util.spec_from_file_location("vault_sentinel", path)
        sentinel = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sentinel)
        ledger = tmp_path / "ledgers" / "proof.jsonl"
        append_jsonl(ledger, {"type": "intact", "value": 1})
        lines = ledger.read_text().splitlines()
        record = json.loads(lines[0])
        record["value"] = 2
        record["entry_hash"] = "b" * 64
        ledger.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")

        result = sentinel.check()
        assert result["ok"] is False
        assert "ledger_chain_broken" in result["issues"]
