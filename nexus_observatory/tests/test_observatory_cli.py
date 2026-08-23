import json

from tools.observatory_cli import DEFAULT_HOME, WAVE_9, NexusObservatory


def fixed_time():
    return "2026-08-24T00:00:00+00:00"


def observatory(tmp_path):
    return NexusObservatory(tmp_path / "home", clock=fixed_time)


class TestNexusAutomation:
    def test_cycle_appends_journal_and_compatible_latest(self, tmp_path):
        nexus = observatory(tmp_path)
        result = nexus.cycle(seed=42)

        assert result["ok"] is True
        assert result["event"]["tick"] == 1
        assert nexus.journal(1)[0]["short_signature"]
        latest = json.loads(nexus.latest_path.read_text())
        assert {"tick", "mood", "chaos", "short_signature"} <= latest.keys()

    def test_second_cycle_increments_and_comparison_reports_delta(self, tmp_path):
        nexus = observatory(tmp_path)
        first = nexus.cycle(seed=1)["event"]
        second = nexus.cycle(seed=2)["event"]
        comparison = nexus.compare()

        assert second["tick"] == first["tick"] + 1
        assert comparison["new_tick"] == second["tick"]
        assert "mood" in comparison["changed_fields"]

    def test_health_requires_valid_telemetry(self, tmp_path):
        home = tmp_path / "home"
        home.mkdir()
        (home / "package.json").write_text("{}", encoding="utf-8")
        (home / "nexus_boot.sh").touch()
        (home / "modules.d").mkdir()
        nexus = NexusObservatory(home, clock=fixed_time)
        (home / "telemetry").mkdir()
        (home / "telemetry" / "resonance.jsonl.latest").write_text("{bad", encoding="utf-8")

        assert nexus.health()["ok"] is False
        nexus.cycle(seed=9)
        assert nexus.health()["ok"] is True

    def test_index_writes_json_markdown_table(self, tmp_path):
        nexus = observatory(tmp_path)
        nexus.cycle(seed=3); nexus.cycle(seed=4)
        report = nexus.index()

        assert report["events"] == 2
        assert report["markdown"].startswith("| Tick |")
        assert json.loads((nexus.telemetry / "index.json").read_text())["events"] == 2

    def test_dashboard_renders_recent_pulses(self, tmp_path):
        nexus = observatory(tmp_path)
        nexus.cycle(seed=5)
        rendered = nexus.dashboard()

        assert rendered.startswith("┌─ NEXUS OBSERVATORY")
        assert (nexus.telemetry / "dashboard.txt").exists()

    def test_dashboard_cli_prints_ascii_not_ci_payload(self, tmp_path, capsys):
        nexus = observatory(tmp_path)
        from tools.observatory_cli import main

        assert main(["--home", str(nexus.home), "dashboard"]) == 0
        captured = capsys.readouterr().out
        assert captured.startswith("┌─ NEXUS OBSERVATORY")
        assert "indexed_events" not in captured

    def test_reliquary_seals_hash_chain(self, tmp_path):
        nexus = observatory(tmp_path)
        for seed in range(3): nexus.cycle(seed=seed)
        relic = nexus.reliquary()

        assert relic["ok"] is True
        assert relic["event_count"] == 3
        assert len(relic["seals"]) == 3
        assert relic["artifact"].endswith(".json")

    def test_watch_runs_requested_cycles_without_sleep_in_unit(self, tmp_path, monkeypatch):
        nexus = observatory(tmp_path)
        monkeypatch.setattr("tools.observatory_cli.time.sleep", lambda seconds: None)
        events = nexus.watch(3, 5000)

        assert [item["event"]["tick"] for item in events] == [1, 2, 3]

    def test_ci_pipeline_is_green_after_cycles(self, tmp_path):
        nexus = observatory(tmp_path)
        # Seed the files required by the repository-level command surface.
        (tmp_path / "home").mkdir(exist_ok=True)
        for source in ("package.json", "nexus_boot.sh"):
            target = nexus.home / source
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((DEFAULT_HOME / source).read_text(), encoding="utf-8")
        modules = nexus.home / "modules.d"
        modules.mkdir(exist_ok=True)
        for module in (DEFAULT_HOME / "modules.d").glob("*.sh"):
            modules.joinpath(module.name).write_text(module.read_text(), encoding="utf-8")

        result = nexus.ci()
        assert result["ok"] is True
        assert result["reliquary"]

    def test_wave_nine_manifest_points_to_existing_commands(self):
        assert len(WAVE_9) == 5
        assert all((__import__("pathlib").Path.cwd() / relative).exists() for relative in WAVE_9)
