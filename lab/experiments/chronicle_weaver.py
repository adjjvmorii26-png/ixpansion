"""Chronicle Weaver — Spins the story of the codebase's evolution.

Reads git history, module creation dates, and wave patterns to weave
a narrative chronicle of how the system came to be.
"""
from __future__ import annotations
import hashlib
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ChronicleWeaver:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.entries: list[dict] = []
        self.chapters: list[dict] = []

    def read_git_history(self) -> list[dict]:
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--all", "-50"],
                capture_output=True, text=True, cwd=str(ROOT), timeout=10
            )
            entries = []
            for line in result.stdout.strip().splitlines():
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    entries.append({"sha": parts[0], "message": parts[1]})
            return entries
        except Exception:
            return []

    def weave_chapters(self, commits: list[dict]) -> list[dict]:
        chapters = []
        wave_commits = [c for c in commits if "wave" in c["message"].lower()]
        other_commits = [c for c in commits if "wave" not in c["message"].lower()]

        if wave_commits:
            chapters.append({
                "title": "The Wave Epoch",
                "description": f"{len(wave_commits)} waves of evolution shaped the system",
                "entries": wave_commits[:10],
                "significance": "high",
            })
        if other_commits:
            chapters.append({
                "title": "The Foundation",
                "description": f"{len(other_commits)} foundational commits built the base",
                "entries": other_commits[:10],
                "significance": "high",
            })

        # Count modules as "civilizations"
        py_count = len(list(ROOT.rglob("*.py")))
        chapters.append({
            "title": "The Civilization Census",
            "description": f"The codebase contains {py_count} Python modules",
            "entries": [],
            "significance": "context",
        })

        return chapters

    def generate_narrative(self) -> str:
        lines = ["═══ CHRONICLE OF IXpansion ═══", ""]
        for ch in self.chapters:
            lines.append(f"📖 {ch['title']}")
            lines.append(f"   {ch['description']}")
            if ch["entries"]:
                for e in ch["entries"][:3]:
                    lines.append(f"   • {e['message'][:60]}")
            lines.append("")
        return "\n".join(lines)

    def report(self) -> dict:
        commits = self.read_git_history()
        self.chapters = self.weave_chapters(commits)
        narrative = self.generate_narrative()
        return {
            "chronicle": "chronicle_weaver",
            "chapter_count": len(self.chapters),
            "commit_count": len(commits),
            "chapters": self.chapters,
            "narrative": narrative,
            "hash": hashlib.md5(narrative.encode()).hexdigest()[:12],
        }


def demo():
    weaver = ChronicleWeaver(seed=42)
    return weaver.report()


def main():
    import json
    result = demo()
    print(result["narrative"])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
