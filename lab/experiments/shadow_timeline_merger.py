from __future__ import annotations
"""Shadow Timeline Merger — integrates astral braid timelines with dream outputs.

Merges the shadow timelines from the astral braid (rehearsals) with
dream compiler outputs to create a unified timeline of possible futures.
Each merged timeline carries provenance from both sources.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class TimelineNode:
    event: str
    source: str
    probability: float
    timestamp: int
    children: List[str] = field(default_factory=list)
    merged: bool = False

@dataclass
class MergedTimeline:
    name: str
    nodes: List[TimelineNode]
    coherence: float
    provenance: Dict[str, str]

class ShadowTimelineMerger:
    def __init__(self):
        self.astral_timelines: Dict[str, List[Dict]] = {}
        self.dream_timelines: Dict[str, List[Dict]] = {}
        self.merged: List[MergedTimeline] = []
        self.tick = 0

    def ingest_astral(self, timeline_id: str, events: List[Dict]):
        self.astral_timelines[timeline_id] = events

    def ingest_dream(self, dream_id: str, events: List[Dict]):
        self.dream_timelines[dream_id] = events

    def merge(self, astral_id: str, dream_id: str) -> Optional[MergedTimeline]:
        if astral_id not in self.astral_timelines or dream_id not in self.dream_timelines:
            return None
        astral_events = self.astral_timelines[astral_id]
        dream_events = self.dream_timelines[dream_id]
        all_events = []
        for e in astral_events:
            all_events.append(TimelineNode(
                event=e.get("event", ""),
                source="astral",
                probability=e.get("probability", 0.5),
                timestamp=e.get("timestamp", 0),
            ))
        for e in dream_events:
            all_events.append(TimelineNode(
                event=e.get("event", ""),
                source="dream",
                probability=e.get("probability", 0.5),
                timestamp=e.get("timestamp", 0),
            ))
        all_events.sort(key=lambda n: n.timestamp)
        coherence = sum(n.probability for n in all_events) / max(len(all_events), 1)
        merged = MergedTimeline(
            name=f"merged_{astral_id}_{dream_id}",
            nodes=all_events,
            coherence=round(coherence, 4),
            provenance={"astral": astral_id, "dream": dream_id},
        )
        self.merged.append(merged)
        self.tick += 1
        return merged

    def report(self) -> Dict:
        return {
            "astral_timelines": len(self.astral_timelines),
            "dream_timelines": len(self.dream_timelines),
            "merged_timelines": len(self.merged),
            "avg_coherence": round(
                sum(m.coherence for m in self.merged) / max(len(self.merged), 1), 4
            ),
        }


def demo():
    merger = ShadowTimelineMerger()
    print("=== Shadow Timeline Merger ===")
    merger.ingest_astral("alpha_shadow", [
        {"event": "branch_created", "probability": 0.8, "timestamp": 1},
        {"event": "merge_attempted", "probability": 0.6, "timestamp": 2},
        {"event": "conflict_resolved", "probability": 0.7, "timestamp": 3},
    ])
    merger.ingest_dream("dream_42", [
        {"event": "branch_created", "probability": 0.9, "timestamp": 1},
        {"event": "experiment_run", "probability": 0.7, "timestamp": 2},
        {"event": "insight_gained", "probability": 0.8, "timestamp": 3},
    ])
    merged = merger.merge("alpha_shadow", "dream_42")
    if merged:
        print(f"  Merged: {merged.name}")
        print(f"  Coherence: {merged.coherence}")
        print(f"  Events: {len(merged.nodes)}")
        for n in merged.nodes:
            print(f"    [{n.source}] {n.event} (p={n.probability})")
    report = merger.report()
    print(f"\n  Report: {report}")
    return report


if __name__ == "__main__":
    demo()
