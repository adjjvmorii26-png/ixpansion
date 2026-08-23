#!/usr/bin/env python3
"""Zero-dependency Nexus automation for pulses, journals, relics, and rituals."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HOME = ROOT / "nexus_observatory"
WAVE_9 = [
    "projects/lab/echolalia.py",
    "projects/lab/schism.py",
    "projects/lab/tide_clock.py",
    "projects/lab/interloper.py",
    "projects/infinity/listening_post.py",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class NexusObservatory:
    def __init__(self, home: Path | None = None, *, clock: Any = utc_now) -> None:
        self.home = home or DEFAULT_HOME
        self.telemetry = self.home / "telemetry"
        self.journal_path = self.telemetry / "nexus-journal.jsonl"
        self.latest_path = self.telemetry / "resonance.jsonl.latest"
        self.clock = clock

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        records: list[dict[str, Any]] = []
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid telemetry at {path}:{number}") from error
        return records

    def journal(self, tail: int = 10) -> list[dict[str, Any]]:
        return self._read_jsonl(self.journal_path)[-tail:]

    def cycle(self, *, seed: int | None = None) -> dict[str, Any]:
        history = self._read_jsonl(self.journal_path)
        sequence = int(history[-1]["tick"]) + 1 if history else 1
        seed = seed if seed is not None else (sequence * 61681)
        moods = ["neutral", "curious", "attentive", "serene"]
        pulse = {
            "source": "nexus-observatory",
            "tick": sequence,
            "mood": moods[sequence % len(moods)],
            "chaos": round(0.40 + ((sequence * 37) % 19) / 100, 4),
            "mesh_events": sequence,
            "created_at": self.clock(),
            "signature": "",
        }
        pulse["signature"] = canonical_hash({key: value for key, value in pulse.items() if key != "signature"})
        pulse["short_signature"] = pulse["signature"][:16]
        self.telemetry.mkdir(parents=True, exist_ok=True)
        with self.journal_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(pulse, sort_keys=True, separators=(",", ":")) + "\n")
        temporary = self.latest_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(pulse, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        os.replace(temporary, self.latest_path)
        return {"ok": True, "event": pulse}

    def health(self) -> dict[str, Any]:
        required = [self.home / "package.json", self.home / "nexus_boot.sh", self.home / "modules.d"]
        checks = {str(path): path.exists() for path in required}
        try:
            events = self.journal(1000)
            journal_ok = True
        except ValueError:
            events = []
            journal_ok = False
        latest_ok = not self.latest_path.exists()
        latest: dict[str, Any] = {}
        if self.latest_path.exists():
            try:
                latest = json.loads(self.latest_path.read_text(encoding="utf-8"))
                latest_ok = all(key in latest for key in ("tick", "mood", "chaos", "short_signature"))
            except (json.JSONDecodeError, OSError):
                latest_ok = False
        writable = True
        try:
            self.telemetry.mkdir(parents=True, exist_ok=True)
            probe = self.telemetry / ".health"
            probe.write_text("ok\n", encoding="utf-8")
            probe.unlink()
        except OSError:
            writable = False
        healthy = all(checks.values()) and journal_ok and latest_ok and writable
        return {
            "ok": healthy,
            "checks": {**checks, "journal_valid": journal_ok, "latest_resonance": latest_ok, "telemetry_writable": writable},
            "events_seen": len(events),
            "latest_tick": latest.get("tick"),
        }

    def index(self) -> dict[str, Any]:
        events = self._read_jsonl(self.journal_path)
        moods: dict[str, int] = {}
        for event in events:
            moods[event["mood"]] = moods.get(event["mood"], 0) + 1
        table = ["| Tick | Mood | Chaos | Signature |", "|---:|---|---:|---|"]
        for event in events[-10:]:
            table.append(f"| {event['tick']} | {event['mood']} | {event['chaos']} | `{event['short_signature']}` |")
        report = {
            "events": len(events),
            "latest_tick": events[-1]["tick"] if events else None,
            "latest_signature": events[-1]["short_signature"] if events else None,
            "moods": moods,
            "markdown": "\n".join(table) + "\n",
        }
        self.telemetry.mkdir(parents=True, exist_ok=True)
        (self.telemetry / "index.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        (self.telemetry / "index.md").write_text(report["markdown"], encoding="utf-8")
        return {"ok": True, **report}

    def compare(self) -> dict[str, Any]:
        events = self._read_jsonl(self.journal_path)[-2:]
        if len(events) != 2:
            raise ValueError("comparison requires two journal pulses")
        old, new = events
        changed = {key: [old.get(key), new.get(key)] for key in old if key in new and old[key] != new[key]}
        return {
            "old_tick": old["tick"],
            "new_tick": new["tick"],
            "changed_fields": sorted(changed),
            "deltas": changed,
            "stable_signature": old["signature"] == new["signature"],
        }

    def dashboard(self) -> str:
        events = self.journal(5)
        latest = events[-1] if events else {"tick": 0, "mood": "silent", "chaos": 0, "short_signature": "-"}
        lines = [
            "┌─ NEXUS OBSERVATORY ───────────────────────────┐",
            f"│ tick      {latest['tick']:<34}│",
            f"│ mood      {latest['mood']:<34}│",
            f"│ chaos     {latest['chaos']:<34}│",
            f"│ signature {latest['short_signature']:<34}│",
            "├─ RECENT PULSES ───────────────────────────────┤",
        ]
        for event in events:
            lines.append(f"│ {event['tick']:>3} · {event['mood']:<14} · {event['short_signature']:<15} │")
        lines.append("└───────────────────────────────────────────────┘")
        rendered = "\n".join(lines)
        (self.telemetry / "dashboard.txt").parent.mkdir(parents=True, exist_ok=True)
        (self.telemetry / "dashboard.txt").write_text(rendered + "\n", encoding="utf-8")
        return rendered

    def creative(self) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        for relative in WAVE_9:
            completed = subprocess.run(
                [sys.executable, str(ROOT / relative)], cwd=ROOT, text=True, capture_output=True, check=False
            )
            parsed: Any = None
            try:
                parsed = json.loads(completed.stdout)
            except json.JSONDecodeError:
                parsed = completed.stdout.strip()
            results.append({
                "script": relative,
                "ok": completed.returncode == 0,
                "exit_code": completed.returncode,
                "result": parsed,
                "stderr": completed.stderr[-400:],
            })
        report = {"wave": 9, "ok": all(item["ok"] for item in results), "results": results}
        self.telemetry.mkdir(parents=True, exist_ok=True)
        (self.telemetry / "wave9.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return report

    def reliquary(self) -> dict[str, Any]:
        events = self._read_jsonl(self.journal_path)
        if not events:
            raise ValueError("no bus events available to seal")
        previous = ""
        sealed = []
        for event in events:
            body = hashlib.sha256((previous + json.dumps(event, sort_keys=True)).encode()).hexdigest()
            sealed.append({"tick": event["tick"], "body_hash": body})
            previous = body
        relic = {
            "sealed_at": self.clock(),
            "event_count": len(events),
            "chain_root": previous,
            "seals": sealed,
        }
        target = self.telemetry / "reliquary" / f"seal-{previous[:12]}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(relic, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return {"ok": True, "artifact": str(target.relative_to(self.home)), **relic}

    def watch(self, cycles: int, interval_ms: int) -> list[dict[str, Any]]:
        if cycles < 1 or interval_ms < 0:
            raise ValueError("cycles must be positive and interval cannot be negative")
        results = []
        for index in range(cycles):
            results.append(self.cycle(seed=index + 1))
            if index + 1 < cycles:
                time.sleep(interval_ms / 1000)
        return results

    def ci(self) -> dict[str, Any]:
        health = self.health()
        cycle = self.cycle(seed=616) if health["ok"] else {"ok": False, "reason": "health_failed"}
        index = self.index() if cycle["ok"] else {}
        reliquary_result = self.reliquary() if cycle["ok"] else {}
        dashboard = self.dashboard() if cycle["ok"] else ""
        return {
            "ok": bool(health["ok"] and cycle["ok"]),
            "health": health,
            "cycle": cycle,
            "indexed_events": index.get("events", 0),
            "reliquary": reliquary_result.get("artifact"),
            "dashboard_lines": len(dashboard.splitlines()),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Nexus Observatory operations")
    parser.add_argument("--home", type=Path, default=DEFAULT_HOME)
    sub = parser.add_subparsers(dest="command", required=True)
    cycle = sub.add_parser("cycle")
    cycle.add_argument("--seed", type=int)
    journal = sub.add_parser("journal")
    journal.add_argument("--tail", type=int, default=10)
    sub.add_parser("health"); sub.add_parser("index"); sub.add_parser("dashboard")
    sub.add_parser("compare"); sub.add_parser("creative"); sub.add_parser("reliquary"); sub.add_parser("ci")
    watch = sub.add_parser("watch")
    watch.add_argument("cycles", type=int, nargs="?", default=3)
    watch.add_argument("interval_ms", type=int, nargs="?", default=5000)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    observatory = NexusObservatory(args.home)
    try:
        if args.command == "cycle":
            result = observatory.cycle(seed=args.seed); print(json.dumps(result, sort_keys=True))
        elif args.command == "journal":
            print(json.dumps({"events": observatory.journal(args.tail)}, sort_keys=True))
        elif args.command == "health":
            result = observatory.health(); print(json.dumps(result, sort_keys=True)); return 0 if result["ok"] else 1
        elif args.command == "index":
            print(json.dumps(observatory.index(), sort_keys=True))
        elif args.command == "compare":
            print(json.dumps(observatory.compare(), sort_keys=True))
        elif args.command == "creative":
            result = observatory.creative(); print(json.dumps(result, sort_keys=True)); return 0 if result["ok"] else 1
        elif args.command == "reliquary":
            print(json.dumps(observatory.reliquary(), sort_keys=True))
        elif args.command == "watch":
            print(json.dumps({"events": observatory.watch(args.cycles, args.interval_ms)}, sort_keys=True))
        elif args.command == "dashboard":
            print(observatory.dashboard())
        else:
            result = observatory.ci(); print(json.dumps(result, sort_keys=True)); return 0 if result["ok"] else 1
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
