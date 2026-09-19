"""HELIX — Growth co-pilot.

Keeps ALEPH moving: next wave numbers, organ gaps, scaffold pressure,
roadmap continuity without breaking dual-track.
Motto: "Growth without rupture."
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
API = ROOT / "api"
DATA = ROOT / "data" / "copilots"
STATE = DATA / "helix_state.json"

WAVE_RE = re.compile(r"^wave(\d+)_([a-z0-9_]+)\.py$")


@dataclass
class Helix:
    name: str = "HELIX"
    role: str = "growth"
    motto: str = "Growth without rupture."
    proposals: list[dict[str, Any]] = field(default_factory=list)

    def survey_waves(self) -> dict[str, Any]:
        waves: list[tuple[int, str]] = []
        if API.is_dir():
            for p in API.glob("wave*.py"):
                m = WAVE_RE.match(p.name)
                if m:
                    waves.append((int(m.group(1)), m.group(2)))
        waves.sort(key=lambda x: x[0])
        nums = [n for n, _ in waves]
        latest = nums[-1] if nums else 0
        gaps = []
        if nums:
            for i in range(min(nums), max(nums) + 1):
                if i not in set(nums) and i > latest - 50:
                    gaps.append(i)
        report = {
            "agent": self.name,
            "role": self.role,
            "ts": datetime.now(timezone.utc).isoformat(),
            "wave_count": len(waves),
            "latest_wave": latest,
            "next_free": latest + 1,
            "recent": [{"n": n, "slug": s} for n, s in waves[-8:]],
            "recent_gaps": gaps[:12],
        }
        self._save(report)
        return report

    def propose_next(self, theme: str | None = None) -> dict[str, Any]:
        survey = self.survey_waves()
        n = int(survey["next_free"])
        theme = (theme or "continuity_braid").strip().lower().replace(" ", "_")[:40]
        backlog = [
            {"slug": "merge_readiness_score", "why": "Score open PRs: organism gates vs external noise"},
            {"slug": "ci_sentinel_bridge", "why": "Wire AEGIS findings into path-filtered lab gates"},
            {"slug": "wave_gap_healer", "why": "Optional fill for recent_gaps without forcing sequential IDs"},
            {"slug": "caption_pipeline_bridge", "why": "QUILL captions -> content_output silent frames for @CoodingLooop"},
        ]
        pick = backlog[n % len(backlog)]
        proposal = {
            "agent": self.name,
            "wave": n,
            "module": f"wave{n}_{pick['slug']}.py",
            "slug": pick["slug"],
            "why": pick["why"],
            "theme_hint": theme,
            "track": "lab",
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        self.proposals.append(proposal)
        return proposal

    def growth_brief(self) -> dict[str, Any]:
        s = self.survey_waves()
        p = self.propose_next()
        return {
            "agent": self.name,
            "motto": self.motto,
            "survey": s,
            "next": p,
            "rules": [
                "Lab experiments land on lab/* path-filtered CI first",
                "Do not collide Council-sealed wave numbers",
                "Prefer specialized substrates over metaphor twins",
                "One mergeable unit per PR — keep ALEPH main velocity unblocked",
            ],
        }

    def _save(self, report: dict) -> None:
        DATA.mkdir(parents=True, exist_ok=True)
        try:
            STATE.write_text(json.dumps(report, indent=2) + "\n")
        except OSError:
            pass


def main() -> None:
    h = Helix()
    print(json.dumps(h.growth_brief(), indent=2))


if __name__ == "__main__":
    main()
