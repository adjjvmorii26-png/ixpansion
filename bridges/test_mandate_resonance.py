import json

import pytest

from bridges.mandate_resonance import build_parser, main, publish, resonate
from lab.pulse_oracle import forecast, seal_oracle
from lab.reversible_mandate import execute
from lab.ritual_parliament import deliberate
from lab.runtime_vault import ledger_path, read_json, state_path


def sandbox_state(entropy=0.90, energy=0.30, ticks=10):
    return {
        "entropy_budget": entropy,
        "novelty": 1.1,
        "ticks": ticks,
        "phase": 0.4,
        "status": "idle",
        "history": [{"tick": index, "energy": energy} for index in range(1, 8)],
    }


def parliament(entropy=0.90):
    sealed_oracle = seal_oracle(forecast(
        sandbox_state=sandbox_state(entropy),
        pulse_state={"beats": 8, "phase": 0.2},
        flux_state={"gen": 2},
        ledger_records=[{"type": "proof"}],
        audit={"ok": True, "tail_hash": "a" * 64},
        horizon=5,
    ))
    return deliberate(sealed_oracle)


def install(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    path = state_path("sandbox", "engine.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sandbox_state()), encoding="utf-8")


class TestMandateResonance:
    def test_sealed_mandate_becomes_nexus_compatible_pulse(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        mandate = execute(parliament())
        pulse = resonate(mandate, clock=lambda: "2026-08-24T00:00:00+00:00")
        assert {"tick", "chaos", "mood", "short_signature"} <= pulse.keys()
        assert pulse["mandate_status"] == "sealed"
        assert pulse["tick"] == 13
        assert pulse["witnesses"] == 3
        assert pulse["signature"] != pulse["short_signature"]

    def test_signature_is_independent_from_transport_time(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        mandate = execute(parliament())
        first = resonate(mandate, clock=lambda: "2026-08-24T00:00:00+00:00")
        second = resonate(mandate, clock=lambda: "2026-08-24T01:00:00+00:00")
        assert first["signature"] == second["signature"]
        assert first["created_at"] != second["created_at"]

    def test_publish_uses_atomic_latest_snapshot(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        mandate = execute(parliament())
        pulse = resonate(mandate)
        destination = tmp_path / "published" / "resonance.latest"
        assert publish(pulse, destination) == destination
        assert json.loads(destination.read_text()) == pulse
        assert destination.read_text().endswith("\n")

    def test_rehearsal_is_clearly_marked_as_a_dream(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        mandate = execute(parliament(), dry_run=True)
        pulse = resonate(mandate)
        assert pulse["mandate_status"] == "rehearsed"
        assert pulse["mood"] == "dreaming"
        assert pulse["tick"] == 13
        assert pulse["witnesses"] == 0

    def test_modified_certificate_fails_closed(self, tmp_path, monkeypatch):
        install(tmp_path, monkeypatch)
        mandate = execute(parliament())
        mandate["execution_certificate"] = "0" * 64
        with pytest.raises(ValueError, match="certificate is missing or modified"):
            resonate(mandate)

    def test_cli_refuses_missing_report_without_publishing(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
        assert main(["--report", str(tmp_path / "absent.json")]) == 1
        result = json.loads(capsys.readouterr().out)
        assert result["ok"] is False
        assert not (tmp_path / "resonance.latest").exists()

    def test_parser_exposes_no_publish_boundary(self):
        assert build_parser().parse_args(["--no-publish"]).no_publish is True
