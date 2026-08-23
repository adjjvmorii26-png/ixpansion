from __future__ import annotations
from collections import Counter
from typing import Any


class ConflictResolver:
    def resolve(self, candidates: list[Any]) -> dict[str, Any]:
        if not candidates:
            raise ValueError("no conflict candidates")
        counts = Counter(str(candidate) for candidate in candidates)
        winner, votes = counts.most_common(1)[0]
        return {"resolved": winner, "votes": votes, "quorum": votes > len(candidates) / 2}
