"""Sandbox Engine: the heartbeat that keeps the organism alive between runs.

Each *tick* of the engine:

1. Asks ``idea_lab`` for a challenge (preferring ones the organism has not
   yet mastered).
2. Drops the challenge's current best-known code -- or its buggy seed on
   first contact -- into a fresh ``world_builder`` cell and scores it.
3. If it fails, hands it to ``self_debugger`` to heal.
4. If it already passes, still spends a little effort trying to *simplify*
   it (shorter, equally-correct code) via evolution, so the organism keeps
   improving even after "solving" something.
5. Records the outcome in a persisted genome file (``sandbox/state/genome.json``
   by default) so history, hall-of-fame code, and cumulative stats survive
   across process restarts -- this is what makes it one continuously
   evolving organism rather than a one-shot script.

Run it directly for a CLI demo:

    python sandbox_engine.py --ticks 5
    python sandbox_engine.py --ticks 20 --use-llm
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from idea_lab import IdeaLab
from llm_bridge import LLMBridge
from self_debugger import SelfDebugger
from world_builder import World

STATE_DIR = Path(__file__).resolve().parent / "state"
DEFAULT_GENOME_PATH = STATE_DIR / "genome.json"


@dataclass
class OrganismRecord:
    """Everything the organism currently knows about one challenge."""

    challenge: str
    best_code: str
    best_fitness: float
    solved: bool
    generation: int = 0
    heals: int = 0
    ticks_seen: int = 0
    last_strategy: Optional[str] = None


@dataclass
class TickLogEntry:
    tick: int
    challenge: str
    fitness_before: float
    fitness_after: float
    healed: bool
    strategy: Optional[str]
    code_length_before: int
    code_length_after: int
    timestamp: float = field(default_factory=time.time)


class Genome:
    """Persisted, cumulative memory of the organism across process runs."""

    def __init__(self, path: Path = DEFAULT_GENOME_PATH):
        self.path = path
        self.records: Dict[str, OrganismRecord] = {}
        self.history: List[TickLogEntry] = []
        self.tick_count = 0
        self.total_heals = 0
        self.born_at = time.time()
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        self.tick_count = raw.get("tick_count", 0)
        self.total_heals = raw.get("total_heals", 0)
        self.born_at = raw.get("born_at", time.time())
        for name, data in raw.get("records", {}).items():
            self.records[name] = OrganismRecord(**data)
        for entry in raw.get("history", []):
            self.history.append(TickLogEntry(**entry))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "born_at": self.born_at,
            "tick_count": self.tick_count,
            "total_heals": self.total_heals,
            "records": {name: asdict(record) for name, record in self.records.items()},
            # Keep the persisted history bounded so the genome file cannot grow forever.
            "history": [asdict(entry) for entry in self.history[-200:]],
        }
        tmp_path = self.path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp_path.replace(self.path)

    def record_for(self, challenge_name: str, seed_code: str) -> OrganismRecord:
        if challenge_name not in self.records:
            self.records[challenge_name] = OrganismRecord(
                challenge=challenge_name,
                best_code=seed_code,
                best_fitness=0.0,
                solved=False,
            )
        return self.records[challenge_name]

    def unsolved_challenges(self) -> List[str]:
        return [name for name, record in self.records.items() if not record.solved]

    def summary(self) -> Dict[str, Any]:
        solved = sum(1 for r in self.records.values() if r.solved)
        return {
            "age_seconds": round(time.time() - self.born_at, 1),
            "tick_count": self.tick_count,
            "total_heals": self.total_heals,
            "challenges_known": len(self.records),
            "challenges_solved": solved,
            "average_fitness": round(
                sum(r.best_fitness for r in self.records.values()) / len(self.records), 4
            )
            if self.records
            else 0.0,
        }


class SandboxEngine:
    """The organism: one tick at a time, forever evolving."""

    def __init__(
        self,
        world: Optional[World] = None,
        idea_lab: Optional[IdeaLab] = None,
        debugger: Optional[SelfDebugger] = None,
        genome: Optional[Genome] = None,
        use_llm: bool = False,
        verbose: bool = True,
    ):
        self.world = world or World()
        llm = LLMBridge() if use_llm else LLMBridge(api_key="", base_url="")
        self.idea_lab = idea_lab or IdeaLab(llm=llm)
        self.debugger = debugger or SelfDebugger(self.world, self.idea_lab, llm=llm)
        self.genome = genome or Genome()
        self.verbose = verbose

    def _log(self, message: str) -> None:
        if self.verbose:
            print(message)

    def tick(self) -> TickLogEntry:
        self.genome.tick_count += 1
        tick_number = self.genome.tick_count

        unsolved = self.genome.unsolved_challenges()
        exclude = [] if not unsolved else [n for n in self.idea_lab.list_challenges() if n not in unsolved]
        challenge = self.idea_lab.propose_challenge(exclude=exclude)

        record = self.genome.record_for(challenge.name, challenge.buggy_seed)
        record.ticks_seen += 1
        code_before = record.best_code
        result_before = self.world.run_harness(code_before, challenge.harness)
        fitness_before = result_before.fitness

        healed = False
        strategy: Optional[str] = None
        best_code, best_result = code_before, result_before

        if not result_before.solved:
            report = self.debugger.heal(code_before, challenge.harness, initial_result=result_before)
            best_code, best_result = report.best_code, report.best_result
            healed = report.healed and not result_before.solved
            strategy = report.strategy_used
            if healed:
                self.genome.total_heals += 1
                record.heals += 1
        else:
            # Already correct: spend effort simplifying without regressing fitness.
            simplified = self._simplify(code_before, challenge.harness, result_before)
            if simplified is not None:
                best_code, best_result = simplified
                strategy = "simplify"

        if best_result.fitness > record.best_fitness or (
            best_result.fitness == record.best_fitness and len(best_code) < len(record.best_code)
        ):
            record.best_code = best_code
            record.best_fitness = best_result.fitness
            record.generation += 1
        record.solved = record.best_fitness >= 1.0
        record.last_strategy = strategy

        entry = TickLogEntry(
            tick=tick_number,
            challenge=challenge.name,
            fitness_before=fitness_before,
            fitness_after=record.best_fitness,
            healed=healed,
            strategy=strategy,
            code_length_before=len(code_before),
            code_length_after=len(record.best_code),
        )
        self.genome.history.append(entry)
        self.genome.save()

        status = "SOLVED" if record.solved else f"fitness {record.best_fitness:.2f}"
        self._log(
            f"[tick {tick_number:04d}] {challenge.name}: "
            f"{fitness_before:.2f} -> {record.best_fitness:.2f} "
            f"({status}, strategy={strategy or 'none'})"
        )
        return entry

    def _simplify(self, code: str, harness: str, current_result):
        """Try a few mutations that keep fitness at 1.0 but shrink the code."""
        best_code, best_result = code, current_result
        for _ in range(8):
            mutant = self.idea_lab.mutate(best_code)
            if mutant == best_code:
                continue
            result = self.world.run_harness(mutant, harness)
            if result.fitness >= current_result.fitness and len(mutant) < len(best_code):
                best_code, best_result = mutant, result
        if best_code != code:
            return best_code, best_result
        return None

    def run(self, ticks: int) -> List[TickLogEntry]:
        return [self.tick() for _ in range(ticks)]

    def status(self) -> Dict[str, Any]:
        summary = self.genome.summary()
        summary["records"] = {
            name: {
                "fitness": record.best_fitness,
                "solved": record.solved,
                "generation": record.generation,
                "heals": record.heals,
            }
            for name, record in sorted(self.genome.records.items())
        }
        return summary


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Run the sandbox organism for a number of ticks.")
    parser.add_argument("--ticks", type=int, default=5, help="Number of evolution ticks to run.")
    parser.add_argument("--use-llm", action="store_true", help="Allow optional LLM-assisted ideas/repair.")
    parser.add_argument("--genome", type=str, default=None, help="Path to a genome JSON file.")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-tick logging.")
    parser.add_argument("--status", action="store_true", help="Print status only, run zero ticks.")
    args = parser.parse_args()

    genome_path = Path(args.genome) if args.genome else DEFAULT_GENOME_PATH
    engine = SandboxEngine(
        genome=Genome(genome_path),
        use_llm=args.use_llm,
        verbose=not args.quiet,
    )

    if not args.status:
        engine.run(args.ticks)

    print(json.dumps(engine.status(), indent=2))


if __name__ == "__main__":
    _cli()
