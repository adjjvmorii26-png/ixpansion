import json

from bridges.counterfactual_twin import CounterfactualTwin, Signal, main
from bridges.divergence_forensics import (
    diagnose_divergence,
    diagnosis_from_twin_outcome,
    diff_state,
)


class TestDivergenceForensics:
    def test_recursive_diff_reports_stable_paths(self):
        deltas = diff_state(
            {"agents": {"a": [1, 2], "b": "old"}, "kept": True},
            {"agents": {"a": [1, 3, 4], "b": "new"}, "kept": True},
        )
        paths = [delta["path"] for delta in deltas]
        assert paths == [
            "$.agents.a[1]", "$.agents.a[2]", "$.agents.b",
        ]
        assert [delta["operation"] for delta in deltas] == [
            "changed", "added", "changed",
        ]

    def test_latent_mutation_has_complete_camouflage(self):
        twin = CounterfactualTwin(seed=42)
        report = twin.run([
            (Signal("agent", 0.1, 0.4), Signal("agent", -0.1, 0.4)),
        ])
        forensics = report["forensics"]

        assert forensics["classification"] == "latent_mutation"
        assert forensics["semantic_changed"] is True
        assert forensics["resonance_changed"] is False
        assert forensics["camouflage_index"] == 1.0
        assert "$.agent.valence" in forensics["changed_paths"]
        assert forensics["containment"][0]["action"] == "mask_and_verify"

    def test_visible_mutation_changes_resonance(self):
        twin = CounterfactualTwin(seed=42)
        report = twin.run([
            (Signal("agent", 0.9, 0.9), Signal("agent", -0.9, 0.9)),
        ])
        forensics = report["forensics"]

        assert forensics["classification"] == "visible_mutation"
        assert forensics["semantic_changed"] is True
        assert forensics["resonance_changed"] is True
        assert "mood" in forensics["changed_status_fields"]
        assert forensics["signature_distance"] > 0

    def test_phantom_signal_detects_telemetry_without_semantics(self):
        diagnosis = diagnose_divergence(
            baseline_state={"same": True},
            twin_state={"same": True},
            baseline_status={"chaos": 0.5, "mood": "neutral", "mesh_events": 0, "reactor_events": 0, "state_keys": 1},
            twin_status={"chaos": 0.5, "mood": "agitated", "mesh_events": 0, "reactor_events": 0, "state_keys": 1},
            baseline_signature="a" * 64,
            twin_signature="b" * 64,
        )
        assert diagnosis.classification == "phantom_signal"
        assert diagnosis.camouflage_index == 0.0
        assert not diagnosis.containment

    def test_persisted_timeline_is_independently_auditable(self, tmp_path):
        output = tmp_path / "twin.json"
        assert main([
            "--seed", "11", "twin", "--output", str(output), "--agent", "audit",
            "--baseline-valence", "0.1", "--baseline-arousal", "0.4",
            "--twin-valence", "-0.2", "--twin-arousal", "0.5",
        ]) == 0
        report = json.loads(output.read_text())
        recomputed = diagnosis_from_twin_outcome(report["timeline"][-1]).payload()

        assert recomputed == report["forensics"]
        assert recomputed["evidence_hash"]

    def test_diagnosis_evidence_is_deterministic(self):
        kwargs = dict(
            baseline_state={"value": 1},
            twin_state={"value": 2},
            baseline_status={"chaos": 0.5, "mood": "neutral", "mesh_events": 0, "reactor_events": 0, "state_keys": 1},
            twin_status={"chaos": 0.5, "mood": "neutral", "mesh_events": 0, "reactor_events": 0, "state_keys": 1},
            baseline_signature="c" * 64,
            twin_signature="d" * 64,
        )
        assert diagnose_divergence(**kwargs).evidence_hash == (
            diagnose_divergence(**kwargs).evidence_hash
        )
