"""Wave 406 — Chronicle Driver.

The organism's memory and event ledger. Records every significant
event, mutation, evolution cycle, and state transition as a
chronicle entry. Maintains the organism's living history.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


class ChronicleDriver:
    """The organism's permanent event ledger and memory system."""

    def __init__(self):
        self.chronicles: List[Dict] = []
        self.epochs: List[Dict] = []
        self.current_epoch = 0
        self.entries_count = 0

    def record(self, event_type: str, data: Dict[str, Any], metadata: Dict = None) -> Dict:
        """Record a chronicle entry."""
        entry = {
            "id": f"chr_{int(time.time() * 1000):016x}",
            "epoch": self.current_epoch,
            "timestamp": time.time(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "data": data,
            "metadata": metadata or {},
            "hash": "",
        }
        entry["hash"] = self._compute_hash(entry)
        self.chronicles.append(entry)
        self.entries_count += 1
        return entry

    def begin_epoch(self, epoch_name: str) -> Dict:
        """Begin a new chronicle epoch."""
        epoch = {
            "id": f"epoch_{self.current_epoch:04d}",
            "name": epoch_name,
            "start_time": time.time(),
            "entries": 0,
        }
        self.epochs.append(epoch)
        self.current_epoch += 1
        return epoch

    def end_epoch(self) -> Dict:
        """End the current epoch."""
        if self.epochs:
            epoch = self.epochs[-1]
            epoch["end_time"] = time.time()
            epoch["duration"] = epoch["end_time"] - epoch["start_time"]
            epoch["entries"] = self.entries_count - epoch.get("entries", 0)
        return epoch

    def get_chronicle(self, limit: int = 100) -> List[Dict]:
        """Retrieve recent chronicle entries."""
        return self.chronicles[-limit:]

    def get_summary(self) -> Dict[str, Any]:
        """Get organism chronicle summary."""
        return {
            "total_entries": self.entries_count,
            "total_epochs": len(self.epochs),
            "current_epoch": self.current_epoch,
            "event_types": self._event_type_counts(),
            "chronicle_density": self.entries_count / max(len(self.epochs), 1),
        }

    def _compute_hash(self, entry: Dict) -> str:
        content = json.dumps({k: v for k, v in entry.items() if k != "hash"}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _event_type_counts(self) -> Dict[str, int]:
        counts = {}
        for e in self.chronicles:
            t = e["event_type"]
            counts[t] = counts.get(t, 0) + 1
        return counts


_driver = None

def get_chronicle() -> ChronicleDriver:
    global _driver
    if _driver is None:
        _driver = ChronicleDriver()
    return _driver

def handler(query: Dict[str, Any] = None) -> Dict[str, Any]:
    chronicle = get_chronicle()
    q = query or {}

    if "action" not in q:
        return {"module": "chronicle_driver", **chronicle.get_summary()}

    action = q["action"]
    if action == "record":
        event_type = q.get("event_type", "unknown")
        data = json.loads(q.get("data", "{}"))
        meta = json.loads(q.get("metadata", "{}"))
        entry = chronicle.record(event_type, data, meta)
        return {"entry": entry}
    elif action == "epoch":
        name = q.get("name", f"epoch_{chronicle.current_epoch}")
        epoch = chronicle.begin_epoch(name)
        return {"epoch": epoch}
    elif action == "end_epoch":
        epoch = chronicle.end_epoch()
        return {"ended_epoch": epoch}
    elif action == "history":
        limit = int(q.get("limit", "100"))
        return {"chronicles": chronicle.get_chronicle(limit)}
    elif action == "summary":
        return chronicle.get_summary()
    else:
        return {"error": f"unknown action: {action}"}
