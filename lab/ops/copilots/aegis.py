"""AEGIS — Guardian co-pilot.

Keeps the mesh alive under stress: CI posture, dual-track separation,
failure triage, fail-closed recommendations.
Motto: \"Nothing merges that cannot be defended.\"
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "copilots"
STATE = DATA / "aegis_state.json"


@dataclass
class Aegis:
    name: str = "AEGIS"
    role: str = "guardian"
    motto: str = "Nothing merges that cannot be defended."
    findings: list[dict[str, Any]] = field(default_factory=list)

    def scan_local(self) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []

        def ok(label: str, passed: bool, detail: str = "") -> None:
            checks.append({"check": label, "ok": passed, "detail": detail})

        ok("repo_root", ROOT.exists(), str(ROOT))
        ok("api_dir", (ROOT / "api").is_dir())
        ok("tests_dir", (ROOT / "tests").is_dir())
        ok("github_workflows", (ROOT / ".github" / "workflows").is_dir())
        dual = ROOT / "docs" / "DUAL_TRACK.md"
        ok("dual_track_doctrine", dual.exists(), "lab gates != full ALEPH CI")
        chaos = ROOT / ".github" / "workflows" / "chaos-monkey.yml"
        ok("chaos_monkey_workflow", chaos.exists())
        resonance = ROOT / ".github" / "workflows" / "resonance-pulse.yml"
        ok("resonance_pulse_workflow", resonance.exists())

        failed = [c for c in checks if not c["ok"]]
        posture = "green" if not failed else ("amber" if len(failed) <= 2 else "red")
        report = {
            "agent": self.name,
            "role": self.role,
            "ts": datetime.now(timezone.utc).isoformat(),
            "posture": posture,
            "checks": checks,
            "actions": self._actions(posture, failed),
        }
        self.findings = checks
        self._save(report)
        return report

    def triage(self, failures: list[str] | None = None) -> dict[str, Any]:
        failures = failures or []
        playbook = {
            "job_summary_closed_file": "Keep summary writes inside with-block; defensive load artifacts",
            "coherence_regulator_state": "Subprocess isolate waves 190-197; never share import state across tests",
            "chaos_timeout": "pytest-timeout + continue-on-error on shuffled seeds; soak still runs",
            "ghas_scanner": "Non-blocking for config-only PRs; do not block vscode/docs packs",
            "proof_garden_cert": "Validate astral-braid certificate_hash before plant()",
            "dual_track_bleed": "Path-filter lab workflows; never require full monorepo suite for lab/*",
        }
        matched = []
        for key, advice in playbook.items():
            if any(key.split("_")[0] in f.lower() or key in f.lower() for f in failures) or not failures:
                matched.append({"class": key, "advice": advice})
        if not failures:
            matched = [{"class": k, "advice": v} for k, v in list(playbook.items())[:4]]
        return {
            "agent": self.name,
            "triage": matched,
            "fail_closed": True,
            "ts": datetime.now(timezone.utc).isoformat(),
        }

    def _actions(self, posture: str, failed: list) -> list[str]:
        acts = []
        if posture == "green":
            acts.append("Hold dual-track; prefer lab path-filtered gates for experimental PRs")
        if failed:
            acts.append(f"Repair missing contracts: {[f['check'] for f in failed]}")
        acts.append("On scheduled red: prefer summary/timeout fixes before domain rewrites")
        acts.append("Block merge only when organism gates fail — not external scanner noise")
        return acts

    def _save(self, report: dict) -> None:
        DATA.mkdir(parents=True, exist_ok=True)
        try:
            STATE.write_text(json.dumps(report, indent=2) + "\n")
        except OSError:
            pass


def main() -> None:
    a = Aegis()
    print(json.dumps({"scan": a.scan_local(), "triage": a.triage()}, indent=2))


if __name__ == "__main__":
    main()
