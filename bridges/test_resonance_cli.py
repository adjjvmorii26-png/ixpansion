import json

from bridges.resonance_cli import main


class TestResonanceCLI:
    def test_observe_outputs_complete_pulse(self, capsys):
        assert main(["--seed", "9", "observe", "--agent", "cli", "--valence", "0.2"]) == 0
        pulse = json.loads(capsys.readouterr().out)
        assert pulse["state_keys"] == 1
        assert len(pulse["signature"]) == 64

    def test_persist_and_analyze_journal(self, tmp_path, capsys):
        journal = tmp_path / "journal.jsonl"
        assert main([
            "--seed", "3", "persist", str(journal), "--label", "first",
        ]) == 0
        assert main([
            "--seed", "3", "persist", str(journal), "--label", "second",
            "--agent", "drift", "--valence", "0.8", "--arousal", "0.9",
        ]) == 0
        capsys.readouterr()

        assert main(["analyze", str(journal)]) == 0
        result = json.loads(capsys.readouterr().out)
        assert result["pulses"] == 2
        assert result["transitions"] in (
            {"mutation": 1}, {"shifting": 1}, {"stable": 1},
        )

    def test_compare_reports_changed_fields(self, tmp_path, capsys):
        old = tmp_path / "old.jsonl"
        new = tmp_path / "new.jsonl"
        main(["--seed", "5", "persist", str(old)])
        main(["--seed", "5", "persist", str(new), "--agent", "new", "--valence", ".7"])
        capsys.readouterr()
        assert main(["compare", str(old), str(new)]) == 0
        result = json.loads(capsys.readouterr().out)
        assert result["changed_fields"] == ["mesh_events", "state_keys"]

    def test_empty_analysis_returns_machine_readable_error(self, tmp_path, capsys):
        empty = tmp_path / "empty.jsonl"
        empty.touch()
        assert main(["analyze", str(empty)]) == 2
        assert "error" in json.loads(capsys.readouterr().out)
