import json

import constellation_dice
import cordyceps
import kintsugi
import negative_space
import mood_superposition


class TestKintsugi:
    def test_repair_honors_scars_and_is_deterministic(self):
        artifact = {"id": "shell", "fractures": [{"id": "a", "length": 3}, {"id": "b", "length": 8}]}
        first = kintsugi.repair(artifact)
        second = kintsugi.repair(artifact)

        assert first == second
        assert first["state"] == "repaired"
        assert [seam["source_fracture"] for seam in first["seams"]] == ["a", "b"]
        assert all(seam["scar_visibility"] == "honored" for seam in first["seams"])

    def test_cli_repairs_demo_artifact(self, capsys):
        assert kintsugi.main([]) == 0
        assert json.loads(capsys.readouterr().out)["repair_fingerprint"]


class TestConstellationDice:
    def test_throw_is_deterministic_and_bounded(self):
        first = constellation_dice.throw_dice(42)
        second = constellation_dice.throw_dice(42)

        assert first == second
        assert first["title"].startswith("The ")
        assert len(first["stars"]) == 5
        assert len({(star["x"], star["y"]) for star in first["stars"]}) == 5

    def test_invalid_star_count_fails_closed(self, capsys):
        assert constellation_dice.main(["--stars", "2"]) == 1
        assert json.loads(capsys.readouterr().out)["ok"] is False

    def test_cli_prints_myth(self, capsys):
        assert constellation_dice.main(["--seed", "7"]) == 0
        assert json.loads(capsys.readouterr().out)["seed"] == 7


class TestCordyceps:
    def test_consent_boundary_stops_spread_and_records_memory(self):
        hosts = [
            {"id": "root", "consent": True, "links": ["open", "sealed"]},
            {"id": "open", "consent": True, "links": []},
            {"id": "sealed", "consent": False, "links": ["beyond"]},
            {"id": "beyond", "consent": True, "links": []},
        ]
        result = cordyceps.spread(hosts, ["root"], 2)

        assert result["state"]["open"] == "expressing"
        assert result["state"]["sealed"] == "immunity-memory"
        assert result["state"]["beyond"] == "dormant"
        assert result["refusal_is_not_failure"] is True

    def test_cli_runs_demo(self, capsys):
        assert cordyceps.main([]) == 0
        assert json.loads(capsys.readouterr().out)["generations"] == 3


class TestNegativeSpace:
    def test_absence_pressures_rank_adjacent_voids_first(self):
        result = negative_space.read_absence([[3, 0], [2, 1], [3, 1], [4, 1], [3, 2]])
        strongest = result["strongest_absences"][0]

        assert result["absence_count"] == 44
        assert (strongest["x"], strongest["y"]) in {(2, 2), (4, 2), (3, 3)}
        assert strongest["adjacent_presence"] >= 1

    def test_out_of_bounds_presence_fails(self):
        import pytest

        with pytest.raises(ValueError):
            negative_space.read_absence([[9, 9]], 3, 3)

    def test_cli_reads_custom_bounds(self, capsys):
        assert negative_space.main(["--width", "5", "--height", "5"]) == 0
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["absence_count"] == 20


class TestMoodSuperposition:
    def test_synthetic_superposition_collapses_dominant_component(self):
        result = mood_superposition.demo()

        assert result["collapsed_label"] == "curiosity"
        assert -1 <= result["blended_valence"] <= 1
        assert result["not_a_claim_of_feeling"] is True

    def test_focus_changes_signature_and_label(self):
        focused = mood_superposition.main(["--focus", "tenderness"])
        assert focused == 0

    def test_empty_mood_is_rejected(self):
        import pytest

        with pytest.raises(ValueError):
            mood_superposition.superpose([])
