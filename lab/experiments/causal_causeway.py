#!/usr/bin/env python3
"""Causal Causeway — build traversal pathways between project structures.

Discovers semantic overlaps between modules across different projects
(ixpansion, omega_fractal_engine, project_root, bridges, mycelium) and
creates weighted causeway links. A causeway allows an agent to "walk"
from one project's concept to a related concept in another project.

This is the first module that explicitly bridges the gap between the
separate project structures in the repo, enabling cross-project
knowledge transfer.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Concept:
    """A concept extracted from a module."""
    concept_id: str
    module_path: str
    project: str
    label: str
    keywords: tuple[str, ...]
    docstring_hash: str

    def payload(self) -> dict[str, Any]:
        return {
            "concept_id": self.concept_id,
            "module_path": self.module_path,
            "project": self.project,
            "label": self.label,
            "keywords": list(self.keywords),
        }


@dataclass(frozen=True)
class Causeway:
    """A weighted pathway between two concepts in different projects."""
    from_concept: str
    to_concept: str
    from_project: str
    to_project: str
    weight: float
    shared_keywords: list[str]
    causeway_id: str

    def payload(self) -> dict[str, Any]:
        return {
            "causeway_id": self.causeway_id,
            "from": self.from_concept,
            "to": self.to_concept,
            "from_project": self.from_project,
            "to_project": self.to_project,
            "weight": round(self.weight, 4),
            "shared_keywords": self.shared_keywords,
        }


def _concept_id(project: str, label: str) -> str:
    raw = f"{project}:{label}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def _extract_keywords(text: str) -> tuple[str, ...]:
    """Extract meaningful keywords from Python source text."""
    words = re.findall(r'[a-z_]{3,}', text.lower())
    stopwords = {
        "the", "and", "for", "that", "this", "with", "from", "import",
        "class", "def", "return", "param", "type", "dataclass", "self",
        "none", "true", "false", "are", "not", "can", "will", "all",
        "when", "has", "but", "was", "its", "any", "into", "our",
        "has", "does", "did", "been", "being", "have", "had", "shall",
        "other", "than", "then", "also", "some", "each", "more", "very",
    }
    return tuple(sorted(set(w for w in words if w not in stopwords))[:20])


def _keyword_overlap(a: tuple[str, ...], b: tuple[str, ...]) -> list[str]:
    return sorted(set(a) & set(b))


@dataclass
class CausewayBuilder:
    """Scan all projects and build cross-project causeways."""
    root: Path
    projects: dict[str, Path] = field(default_factory=dict)
    min_shared_keywords: int = 2
    min_causeway_weight: float = 0.1

    def __post_init__(self) -> None:
        if not self.projects:
            self.projects = {
                "ixpansion": self.root / "ixpansion",
                "omega_fractal": self.root / "omega_fractal_engine",
                "project_root": self.root / "project_root",
                "bridges": self.root / "bridges",
                "mycelium": self.root / "mycelium",
                "omega_prime": self.root / "omega_prime",
                "lab": self.root / "lab",
                "constellation": self.root / "constellation",
            }

    def build(self) -> dict[str, Any]:
        concepts = self._extract_all_concepts()
        causeways = self._find_causeways(concepts)
        graph = self._build_graph(concepts, causeways)

        return {
            "concepts": [c.payload() for c in concepts],
            "causeways": [cw.payload() for cw in causeways],
            "graph": graph,
            "summary": {
                "total_concepts": len(concepts),
                "total_causeways": len(causeways),
                "projects_connected": len(set(
                    cw.from_project for cw in causeways
                ) | set(cw.to_project for cw in causeways)),
                "strongest_causeway": causeways[0].payload() if causeways else None,
                "project_pairs": list(set(
                    tuple(sorted([cw.from_project, cw.to_project]))
                    for cw in causeways
                )),
            },
        }

    def _extract_all_concepts(self) -> list[Concept]:
        concepts: list[Concept] = []
        for project_name, project_path in self.projects.items():
            if not project_path.is_dir():
                continue
            for py_file in project_path.rglob("*.py"):
                if "__pycache__" in str(py_file) or "test_" in py_file.name:
                    continue
                try:
                    source = py_file.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue

                # Extract class/function names as concept labels
                labels = set()
                for line in source.split("\n"):
                    stripped = line.strip()
                    if stripped.startswith("class "):
                        label = stripped.split("(")[0].replace("class ", "").strip()
                        labels.add(label)
                    elif stripped.startswith("def ") and not stripped.startswith("def _"):
                        label = stripped.split("(")[0].replace("def ", "").strip()
                        labels.add(label)

                if not labels:
                    # Use the filename as concept
                    labels = {py_file.stem}

                keywords = _extract_keywords(source)
                docstring_hash = hashlib.sha256(
                    source[:500].encode()
                ).hexdigest()[:8]

                for label in labels:
                    concepts.append(Concept(
                        concept_id=_concept_id(project_name, label),
                        module_path=str(py_file.relative_to(self.root)),
                        project=project_name,
                        label=label,
                        keywords=keywords,
                        docstring_hash=docstring_hash,
                    ))

        return concepts

    def _find_causeways(self, concepts: list[Concept]) -> list[Causeway]:
        causeways: list[Causeway] = []
        seen: set[tuple[str, str]] = set()

        for i, c_a in enumerate(concepts):
            for c_b in concepts[i + 1:]:
                if c_a.project == c_b.project:
                    continue
                pair = tuple(sorted([c_a.concept_id, c_b.concept_id]))
                if pair in seen:
                    continue
                seen.add(pair)

                shared = _keyword_overlap(c_a.keywords, c_b.keywords)
                if len(shared) < self.min_shared_keywords:
                    continue

                weight = len(shared) / max(len(c_a.keywords), len(c_b.keywords), 1)
                if weight < self.min_causeway_weight:
                    continue

                cw_id = hashlib.sha256(
                    f"{c_a.concept_id}:{c_b.concept_id}".encode()
                ).hexdigest()[:12]

                causeways.append(Causeway(
                    from_concept=c_a.concept_id,
                    to_concept=c_b.concept_id,
                    from_project=c_a.project,
                    to_project=c_b.project,
                    weight=weight,
                    shared_keywords=shared,
                    causeway_id=cw_id,
                ))

        return sorted(causeways, key=lambda cw: -cw.weight)[:50]

    def _build_graph(self, concepts: list[Concept], causeways: list[Causeway]) -> dict[str, Any]:
        concept_map = {c.concept_id: c for c in concepts}

        project_connections = defaultdict(int)
        for cw in causeways:
            pair = tuple(sorted([cw.from_project, cw.to_project]))
            project_connections[pair] += 1

        return {
            "project_connections": {
                f"{k[0]}<->{k[1]}": v
                for k, v in sorted(project_connections.items(), key=lambda x: -x[1])
            },
            "hub_projects": sorted(
                defaultdict(int, {
                    proj: sum(
                        1 for cw in causeways
                        if cw.from_project == proj or cw.to_project == proj
                    )
                    for proj in set(c.project for c in concepts)
                }).items(),
                key=lambda x: -x[1],
            )[:5],
        }


def demo() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    builder = CausewayBuilder(root=root)
    return builder.build()


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
