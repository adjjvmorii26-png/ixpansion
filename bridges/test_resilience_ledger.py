import json

from bridges.counterfactual_twin import Signal
from bridges.resilience_ledger import ResilienceLedger, main


class TestResilienceLedger:
    def test_matching_experience_produces_elastic_recovery(self):
        report = ResilienceLedger(seed=42).probe_single(
            Signal("agent", 0.1, 0.4),
            Signal("agent", -0.1, 0.4),
            Signal("agent", 0.0, 0.5),
            recovery_steps=2,
        )

        assert report["classification"] == "elastic_recovery"
        assert report["semantic_recovered_after_experiences"] == 1
        assert report["final_semantic_recovered"] is True
        assert report["final_resonance_recovered"] is True
        assert report["recovery_efficiency"] == 1.0

    def test_multiple_wounds_can_require_delayed_recovery(self):
        ledger = ResilienceLedger(seed=42)
        report = ledger.probe(
            [
                (Signal("alpha", 0.1, 0.4), Signal("alpha", -0.1, 0.4)),
                (Signal("beta", 0.2, 0.4), Signal("beta", -0.2, 0.4)),
            ],
            [Signal("alpha", 0.0, 0.5), Signal("beta", 0.0, 0.5)],
        )

        assert report["classification"] == "delayed_recovery"
        assert report["semantic_recovered_after_experiences"] == 2
        assert report["recovery_timeline"][0]["semantic_changed"] is True
        assert report["recovery_timeline"][1]["semantic_changed"] is False

    def test_telemetry_can_heal_while_exact_history_remains_hysteretic(self):
        report = ResilienceLedger(seed=42).probe_single(
            Signal("agent", 0.9, 0.9),
            Signal("agent", -0.9, 0.9),
            Signal("observer", 0.0, 0.5),
            recovery_steps=1,
        )

        assert report["classification"] == "hysteretic_trace"
        assert report["final_semantic_recovered"] is False
        assert report["final_resonance_recovered"] is True
        assert report["final_state"]["changed_paths"]

    def test_unrepaired_wound_remains_plastic(self):
        report = ResilienceLedger(seed=42).probe_single(
            Signal("agent", 0.9, 0.9),
            Signal("agent", -0.9, 0.9),
            Signal("observer", 0.0, 0.5),
            recovery_steps=0,
        )

        assert report["classification"] == "plastic_divergence"
        assert report["final_semantic_recovered"] is False
        assert report["final_resonance_recovered"] is False
        assert report["recovery_timeline"] == []

    def test_identical_perturbation_is_inert(self):
        report = ResilienceLedger(seed=42).probe_single(
            Signal("agent", 0.25, 0.65),
            Signal("agent", 0.25, 0.65),
            Signal("agent", 0.0, 0.5),
        )

        assert report["classification"] == "inert_perturbation"
        assert report["initial_wound"]["semantic_changed"] is False
        assert report["recovery_efficiency"] == 1.0

    def test_cli_artifact_is_deterministic_and_complete(self, tmp_path):
        output = tmp_path / "resilience.json"
        args = [
            "--seed", "11", "probe", "--output", str(output), "--agent", "probe",
            "--baseline-valence", "0.1", "--baseline-arousal", "0.4",
            "--twin-valence", "-0.1", "--twin-arousal", "0.5",
            "--recovery-valence", "0", "--recovery-arousal", "0.5",
            "--recovery-steps", "2",
        ]
        assert main(args) == 0
        first = json.loads(output.read_text())
        output.unlink()
        assert main(args) == 0
        second = json.loads(output.read_text())

        assert first["classification"] == second["classification"]
        assert first["evidence_hash"] == second["evidence_hash"]
        assert len(first["recovery_timeline"]) == 2
