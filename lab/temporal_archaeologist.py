"""Temporal Archaeologist — Digs through git history for hidden patterns.

Mines commit history for patterns, correlations, and insights that
reveal how the codebase evolved and what drove its development.
"""
from __future__ import annotations
import hashlib
import subprocess
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TemporalArchaeologist:
    def __init__(self, seed=42):
        self.seed = seed
        self.commits: list[dict] = []
        self.artifacts: list[dict] = []

    def excavate(self) -> list[dict]:
        try:
            result = subprocess.run(
                ["git", "log", "--all", "--format=%H|%s|%ai", "-200"],
                capture_output=True, text=True, cwd=str(ROOT), timeout=15
            )
            for line in result.stdout.strip().splitlines():
                parts = line.split("|", 2)
                if len(parts) == 3:
                    self.commits.append({
                        "sha": parts[0][:8], "message": parts[1],
                        "date": parts[2], "wave": self._extract_wave(parts[1]),
                    })
        except Exception:
            pass
        return self.commits

    def _extract_wave(self, message: str) -> int | None:
        words = message.lower().split()
        for i, w in enumerate(words):
            if w == "wave" and i + 1 < len(words) and words[i+1].isdigit():
                return int(words[i+1])
        return None

    def analyze_era_boundaries(self) -> list[dict]:
        waves = [(c["wave"], c) for c in self.commits if c["wave"] is not None]
        boundaries = []
        for i in range(len(waves) - 1):
            if waves[i][0] != waves[i+1][0]:
                boundaries.append({
                    "from_wave": waves[i+1][0], "to_wave": waves[i][0],
                    "transition_message": waves[i][1]["message"][:60],
                })
        return boundaries

    def analyze_commit_patterns(self) -> dict:
        words = []
        for c in self.commits:
            words.extend(c["message"].lower().split())
        word_freq = Counter(words)
        return {
            "total_commits": len(self.commits),
            "top_words": word_freq.most_common(15),
            "wave_commits": sum(1 for c in self.commits if c["wave"]),
            "non_wave_commits": sum(1 for c in self.commits if not c["wave"]),
        }

    def discover_hidden_patterns(self) -> list[dict]:
        patterns = []
        wave_sizes = Counter()
        for c in self.commits:
            if c["wave"]:
                wave_sizes[c["wave"]] += 1
        if wave_sizes:
            sizes = list(wave_sizes.values())
            avg = sum(sizes) / len(sizes)
            for wave, count in wave_sizes.items():
                if count > avg * 1.5:
                    patterns.append({
                        "pattern": "large_wave", "wave": wave,
                        "detail": f"Wave {wave} had {count} commits (avg: {avg:.1f})",
                        "significance": "high",
                    })
        return patterns

    def report(self) -> dict:
        self.excavate()
        patterns = self.discover_hidden_patterns()
        return {
            "archaeologist": "temporal_archaeologist",
            "commits_analyzed": len(self.commits),
            "waves_found": len(set(c["wave"] for c in self.commits if c["wave"])),
            "patterns": patterns,
            "era_boundaries": self.analyze_era_boundaries()[:5],
            "commit_patterns": self.analyze_commit_patterns(),
        }


def demo():
    arch = TemporalArchaeologist(seed=42)
    return arch.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
