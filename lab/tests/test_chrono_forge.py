import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_script(relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_manifest():
    return json.loads(Path("lab/pinned_projects.json").read_text())


class TestChronoForgePort:
    def test_pinned_manifest_is_unique_and_executable(self):
        data = load_manifest()
        projects = data["projects"]
        assert len(projects) == 15
        assert len({item["id"] for item in projects}) == len(projects)
        assert all((Path(item["path"]).is_file()) for item in projects)
        assert sum(item["critical"] for item in projects) == 5

    def test_evolution_automations_are_advisory_and_consent_is_manual(self):
        data = load_manifest()
        ids = [item["id"] for item in data["projects"]]
        assert ids.index("ritual_parliament") < ids.index("genome_atlas") < ids.index("evolution_council")
        assert all(item["path"] != "lab/evolution_consent.py" for item in data["projects"])

    def test_critical_runner_records_four_successful_entries(self, tmp_path, monkeypatch):
        import lab.run_pinned as runner

        monkeypatch.setattr(runner, "REPORT", tmp_path / "report.json")
        monkeypatch.setattr(runner, "LEDGER", tmp_path / "ledger.jsonl")
        assert runner.main(["--critical-only"]) == 0
        report = json.loads((tmp_path / "report.json").read_text())
        assert report["ok"] is True
        assert [entry["id"] for entry in report["results"]] == ["lab_smoke", "pulse", "sentinel", "sandbox_status", "sandbox_tick"]
        assert all(entry["ok"] for entry in report["results"])
        assert (tmp_path / "ledger.jsonl").exists()

    def test_forge_mind_is_symbolic_and_deterministic(self):
        forge_mind = load_script("lab/chrono_forge/2_agents/forge_mind.py")
        first = forge_mind.respond("NODE status")
        second = forge_mind.respond(" node   status ")
        assert first["ritual"] == "observe"
        assert {key: value for key, value in first.items() if key != "input"} == {
            key: value for key, value in second.items() if key != "input"
        }
        assert load_script("lab/chrono_forge/2_agents/forge_mind.py").respond("error: repair the fracture")["ritual"] == "repair"

    def test_unknown_phrase_becomes_preserved_anomaly(self):
        result = load_script("lab/chrono_forge/2_agents/forge_mind.py").respond("unmapped signal")
        assert result["ritual"] == "witness"
        assert result["response"] == "preserve the phrase as an unresolved anomaly"
        assert result["fingerprint"]

    def test_pulse_uses_injected_state_and_advances_sigils(self, tmp_path, monkeypatch):
        pulse_driver = load_script("lab/chrono_forge/0_primal_core/pulse_driver.py")
        monkeypatch.setattr(pulse_driver, "STATE", tmp_path / "state.json")
        state = pulse_driver.pulse(2)
        assert state["beats"] == 2
        assert state["sigil"] == "PULSE-0002"
        assert (tmp_path / "state.json").exists()

    def test_sandbox_entropy_budget_remains_above_floor(self, tmp_path, monkeypatch):
        from sandbox import sandbox_engine

        monkeypatch.setattr(sandbox_engine, "STATE", tmp_path / "sandbox_state.json")
        state = sandbox_engine.run_ticks(2, proof=False)
        assert state["ticks"] == 2
        assert state["entropy_budget"] >= 0.05
        assert len(state["history"]) == 2

    def test_cli_portal_help_lists_all_acts(self, capsys):
        cli_portal = load_script("lab/chrono_forge/5_interfaces/cli_portal.py")
        assert cli_portal.main(["help"]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert {"invoke", "flux", "mirror", "smoke"}.issubset(payload["acts"])

    def test_scheduled_workflow_avoids_direct_input_interpolation(self):
        workflow = Path(".github/workflows/pinned-lab.yml").read_text()
        assert "CRITICAL_ONLY: ${{ github.event.inputs.critical_only || 'false' }}" in workflow
        assert '[ "${{ github.event.inputs.critical_only }}" = "true" ]' not in workflow
