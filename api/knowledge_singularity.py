"""Wave 120 — Knowledge Singularity Convergence.

Approaches a unified representation of all system knowledge by iteratively
merging, deduplicating, and synthesising knowledge fragments into
increasingly compact and information-dense structures.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class KnowledgeFragment:
    """A single piece of knowledge in the system."""

    def __init__(self, domain: str, content: str, confidence: float = 1.0):
        self.domain = domain
        self.content = content
        self.confidence = confidence
        self.created = time.time()
        self.hash = hashlib.sha256(f"{domain}:{content}".encode()).hexdigest()[:12]
        self.merged_into: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "content": self.content,
            "confidence": self.confidence,
            "hash": self.hash,
            "merged_into": self.merged_into,
        }


class KnowledgeSingularity:
    """Iteratively merges knowledge fragments toward a unified representation."""

    def __init__(self):
        self._fragments: Dict[str, KnowledgeFragment] = {}
        self._merge_rounds = 0
        self._synthesis_log: List[str] = []

    @property
    def fragment_count(self) -> int:
        return sum(1 for f in self._fragments.values() if f.merged_into is None)

    def ingest(self, domain: str, content: str, confidence: float = 1.0) -> KnowledgeFragment:
        frag = KnowledgeFragment(domain=domain, content=content, confidence=confidence)
        self._fragments[frag.hash] = frag
        return frag

    def find_related(self, fragment: KnowledgeFragment) -> List[KnowledgeFragment]:
        related = []
        for f in self._fragments.values():
            if f.hash == fragment.hash or f.merged_into is not None:
                continue
            if f.domain == fragment.domain:
                related.append(f)
        return related

    def merge(self, a: KnowledgeFragment, b: KnowledgeFragment) -> KnowledgeFragment:
        merged_content = f"{a.content} + {b.content}"
        merged_confidence = min(1.0, (a.confidence + b.confidence) / 2 + 0.1)
        merged = KnowledgeFragment(
            domain=a.domain,
            content=merged_content,
            confidence=merged_confidence,
        )
        a.merged_into = merged.hash
        b.merged_into = merged.hash
        self._fragments[merged.hash] = merged
        self._synthesis_log.append(
            f"Merged {a.hash}+{b.hash} -> {merged.hash} in {a.domain}"
        )
        return merged

    def convergence_round(self) -> int:
        self._merge_rounds += 1
        merged_count = 0
        seen_domains: Dict[str, List[KnowledgeFragment]] = {}
        for f in self._fragments.values():
            if f.merged_into is not None:
                continue
            seen_domains.setdefault(f.domain, []).append(f)
        for domain, frags in seen_domains.items():
            if len(frags) >= 2:
                self.merge(frags[0], frags[1])
                merged_count += 1
        return merged_count

    def singularity_distance(self) -> float:
        active = self.fragment_count
        if active <= 1:
            return 0.0
        return 1.0 - (1.0 / active)

    def get_fragments(self) -> List[Dict[str, Any]]:
        return [f.to_dict() for f in self._fragments.values()]

    def status(self) -> Dict[str, Any]:
        return {
            "active_fragments": self.fragment_count,
            "total_fragments": len(self._fragments),
            "merge_rounds": self._merge_rounds,
            "synthesis_events": len(self._synthesis_log),
            "singularity_distance": self.singularity_distance(),
        }
