import json

from bridges.counterfactual_twin import CounterfactualTwin, Signal, main


class TestCounterfactualTwin:
    def test_identical_signals_do_not_split(self):
        twin = CounterfactualTwin(seed=42)
        report = twin.run([(Signal("scout", 0.4, 0.7), Signal("scout", 0.4, 0.7))])

        assert report["divergence"] is None
        assert report["final"]["semantic_match"] is True
        assert report["final"]["resonance_match"] is True
        assert len(report["timeline"]) == 1

    def test_semantic_split_precedes_resonance_visibility(self):
        twin = CounterfactualTwin(seed=42)
        report = twin.run([
            (Signal("ghost", 0.1, 0.4), Signal("ghost", -0.1, 0.4)),
        ])
        boundary = report["divergence"]

        assert boundary is not None
        assert boundary["kind"] == "semantic"
        assert boundary["step_index"] == 1
        assert boundary["state_changed"] is True
        # Neither mood nor any coarse telemetry field changed yet.
        assert boundary["resonance_changed"] is False
        assert report["final"]["semantic_match"] is False

    def test_first_divergence_is_preserved_across_steps(self):
        twin = CounterfactualTwin(seed=42)
        report = twin.run([
            (Signal("agent", 0.1, 0.4), Signal("agent", 0.1, 0.4)),
            (Signal("agent", 0.9, 0.9), Signal("agent", -0.9, 0.9)),
        ])

        assert report["divergence"]["kind"] == "semantic"
        assert report["divergence"]["step_index"] == 2
        assert len(report["timeline"]) == 2
        assert report["final"]["distance"] > 0

    def test_cli_writes_deterministic_artifact(self, tmp_path, capsys):
        output = tmp_path / "twin.json"
        args = [
            "--seed", "7", "twin", "--output", str(output), "--agent", "probe",
            "--baseline-valence", "0.1", "--baseline-arousal", "0.4",
            "--twin-valence", "-0.1", "--twin-arousal", "0.4",
        ]
        assert main(args) == 0
        first = json.loads(output.read_text())
        summary = json.loads(capsys.readouterr().out)
        assert summary["report_hash"] == first["report_hash"]

        output.unlink()
        assert main(args) == 0
        capsys.readouterr()
        second = json.loads(output.read_text())
        assert second["report_hash"] == first["report_hash"]

    def test_empty_spec_returns_machine_readable_error(self, tmp_path, capsys):
        spec = tmp_path / "empty.json"
        spec.write_text('{"interventions":[]}', encoding="utf-8")
        assert main([
            "--seed", "1", "twin", "--output", str(tmp_path / "out.json"),
            "--spec", str(spec),
        ]) == 2
        assert "error" in json.loads(capsys.readouterr().out)
