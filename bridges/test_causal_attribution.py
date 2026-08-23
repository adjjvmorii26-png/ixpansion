import json

from bridges.causal_attribution import CausalAttributor, main
from bridges.counterfactual_twin import Signal


class TestCausalAttribution:
    def test_single_difference_is_direct_cause(self):
        report = CausalAttributor(seed=42).run([
            (Signal("agent", 0.1, 0.4), Signal("agent", -0.1, 0.4)),
        ])
        verdict = report["verdicts"][0]

        assert report["observed_target_diverged"] is True
        assert verdict["classification"] == "direct_cause"
        assert verdict["necessary"] is True
        assert verdict["sufficient"] is True
        assert verdict["causal_mass"] == 1.0
        assert verdict["changed_path_overlap"] == 1.0

    def test_parallel_alternative_routes_are_recognized(self):
        report = CausalAttributor(seed=42).run([
            (Signal("alpha", 0.2, 0.4), Signal("alpha", -0.2, 0.4)),
            (Signal("beta", 0.3, 0.4), Signal("beta", -0.3, 0.4)),
        ])

        assert [item["classification"] for item in report["verdicts"]] == [
            "alternative_route", "alternative_route",
        ]
        assert all(item["necessary"] is False for item in report["verdicts"])
        assert all(item["sufficient"] is True for item in report["verdicts"])
        assert all(item["causal_mass"] == 0.5 for item in report["verdicts"])

    def test_resonance_target_ignores_invisible_semantic_split(self):
        report = CausalAttributor(seed=42, target="resonance").run([
            (Signal("agent", 0.1, 0.4), Signal("agent", -0.1, 0.4)),
        ])
        verdict = report["verdicts"][0]

        assert report["observed_target_diverged"] is False
        assert verdict["classification"] == "dormant_potential"
        assert verdict["causal_mass"] == 0.0

    def test_resonance_target_detects_visible_split(self):
        report = CausalAttributor(seed=42, target="resonance").run([
            (Signal("agent", 0.9, 0.9), Signal("agent", -0.9, 0.9)),
        ])
        verdict = report["verdicts"][0]

        assert report["observed_target_diverged"] is True
        assert verdict["classification"] == "direct_cause"
        assert verdict["full_first_kind"] == "semantic"

    def test_replays_are_deterministic(self):
        interventions = [
            (Signal("agent", 0.25, 0.65), Signal("agent", -0.35, 0.75)),
            (Signal("echo", 0.15, 0.45), Signal("echo", -0.15, 0.55)),
        ]
        first = CausalAttributor(seed=7).run(interventions)
        second = CausalAttributor(seed=7).run(interventions)

        assert first["report_hash"] == second["report_hash"]
        assert first["causal_fingerprint"] == second["causal_fingerprint"]

    def test_cli_loads_spec_and_writes_atomic_artifact(self, tmp_path):
        spec = tmp_path / "interventions.json"
        output = tmp_path / "attribution.json"
        spec.write_text(json.dumps({
            "interventions": [{
                "agent": "probe",
                "baseline": {"valence": 0.1, "arousal": 0.4},
                "twin": {"valence": -0.2, "arousal": 0.5},
            }]
        }), encoding="utf-8")
        assert main([
            "--seed", "13", "attribute", "--spec", str(spec),
            "--output", str(output), "--target", "semantic",
        ]) == 0
        report = json.loads(output.read_text())
        assert report["verdicts"][0]["classification"] == "direct_cause"
