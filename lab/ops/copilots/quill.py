"""QUILL — Continuity co-pilot.

Holds the story together: status briefs, doctrine lines, silent captions,
PR language that matches ALEPH without drowning in noise.
Motto: \"What is not written dissolves.\"
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "copilots"
STATE = DATA / "quill_state.json"
HEARTBEAT = ROOT / "docs" / "LAB_HEARTBEAT.json"


@dataclass
class Quill:
    name: str = "QUILL"
    role: str = "continuity"
    motto: str = "What is not written dissolves."

    def caption(self, frames: list[str], *, channel: str = "@CoodingLooop") -> dict[str, Any]:
        lines = [str(f)[:120] for f in frames[:12]]
        return {
            "agent": self.name,
            "channel": channel,
            "style": "silent_caption_only",
            "frames": [{"t": i * 2, "text": line} for i, line in enumerate(lines)],
            "ts": datetime.now(timezone.utc).isoformat(),
        }

    def brief(self, *, aegis: dict | None = None, helix: dict | None = None, extra: str = "") -> dict[str, Any]:
        posture = (aegis or {}).get("posture", "unknown")
        latest = (helix or {}).get("survey", {}).get("latest_wave") or (helix or {}).get("latest_wave")
        next_w = (helix or {}).get("next", {})
        lines = [
            f"ALEPH co-pilot council · posture {posture}",
            f"latest wave {latest} · next {next_w.get('wave', '?')} {next_w.get('slug', '')}",
            "AEGIS guards · HELIX grows · QUILL remembers",
        ]
        if extra:
            lines.append(extra[:120])
        doc = {
            "agent": self.name,
            "role": self.role,
            "ts": datetime.now(timezone.utc).isoformat(),
            "posture": posture,
            "headline": lines[0],
            "bullets": lines[1:],
            "caption": self.caption(lines),
            "doctrine": [
                "lab_gates_neq_aleph_ci",
                "silence_is_product",
                "fail_closed_on_organism_gates",
                "external_scanner_noise_is_not_merge_blocker",
            ],
        }
        self._save(doc)
        self._heartbeat(doc)
        return doc

    def pr_body_stub(self, title: str, changes: list[str]) -> str:
        bullets = "\n".join(f"- {c}" for c in changes[:12])
        return (
            f"## {title}\n\n{bullets}\n\n"
            f"### Co-pilot notes\n"
            f"- **AEGIS**: organism gates only; dual-track preserved\n"
            f"- **HELIX**: growth unit scoped; no wave-number collision intent\n"
            f"- **QUILL**: silent captions / doctrine unchanged unless listed\n\n"
            f"Caption: `aegis · helix · quill`\n"
        )

    def _heartbeat(self, doc: dict) -> None:
        try:
            HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
            HEARTBEAT.write_text(json.dumps({
                "updated": doc["ts"],
                "posture": doc.get("posture"),
                "headline": doc.get("headline"),
                "council": ["AEGIS", "HELIX", "QUILL"],
            }, indent=2) + "\n")
        except OSError:
            pass

    def _save(self, report: dict) -> None:
        DATA.mkdir(parents=True, exist_ok=True)
        try:
            STATE.write_text(json.dumps(report, indent=2) + "\n")
        except OSError:
            pass


def main() -> None:
    q = Quill()
    print(json.dumps(q.brief(extra="council online"), indent=2))


if __name__ == "__main__":
    main()
