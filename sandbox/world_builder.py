"""World Builder: disposable, isolated execution cells for the sandbox organism.

Every idea the organism has is born into its own throwaway "cell": a fresh
temporary directory, a stripped-down environment with no inherited secrets,
a wall-clock timeout, and (on POSIX) CPU-time and memory limits. The cell
runs, reports back, and is deleted. Nothing it does persists except the
structured result handed back to the caller.

This module intentionally has zero third-party dependencies so the organism
never needs an API key or network access to stay alive.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - resource is POSIX-only
    import resource
except ImportError:  # pragma: no cover
    resource = None


RESULT_MARKER = "SANDBOX_RESULT_JSON="


@dataclass
class ExecutionResult:
    """The outcome of running one piece of code inside a cell."""

    success: bool
    exit_code: Optional[int]
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool
    result: Optional[Dict[str, Any]] = None

    @property
    def fitness(self) -> float:
        """Fraction of harness test cases passed, 0.0 if the cell never ran."""
        if not self.result:
            return 0.0
        total = self.result.get("total") or 0
        if not total:
            return 0.0
        return float(self.result.get("passed", 0)) / float(total)

    @property
    def solved(self) -> bool:
        """True only when the cell executed cleanly AND every case passed.

        ``success`` alone just means the harness ran without crashing or
        timing out and produced a parseable result -- a candidate can run
        "successfully" while still failing most of its test cases. ``solved``
        is the stricter, behavior-complete signal the engine and debugger
        use to decide whether a challenge is actually finished.
        """
        return self.success and self.fitness >= 1.0


@dataclass
class Cell:
    """A single generation-tagged unit of candidate code."""

    id: str
    code: str
    generation: int = 0
    parent_id: Optional[str] = None
    origin: str = "seed"
    created_at: float = field(default_factory=time.time)


def _restricted_environment() -> Dict[str, str]:
    """Build a minimal environment with no inherited API keys or secrets."""
    keep = {"PATH", "LANG", "LC_ALL", "SYSTEMROOT", "PYTHONIOENCODING"}
    env = {key: value for key, value in os.environ.items() if key in keep}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    return env


def _limit_resources(cpu_seconds: int, memory_mb: int):
    """Return a preexec_fn that caps CPU time and address space (POSIX only)."""

    def _apply():  # pragma: no cover - exercised only inside subprocess
        if resource is None:
            return
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        except (ValueError, OSError):
            pass
        try:
            limit_bytes = memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))
        except (ValueError, OSError):
            pass
        try:
            resource.setrlimit(resource.RLIMIT_NPROC, (32, 32))
        except (ValueError, OSError):
            pass

    return _apply


class World:
    """A sealed environment that can grow and reap disposable code cells."""

    def __init__(
        self,
        timeout: float = 5.0,
        cpu_seconds: int = 4,
        memory_mb: int = 256,
        root: Optional[str] = None,
    ):
        self.timeout = timeout
        self.cpu_seconds = cpu_seconds
        self.memory_mb = memory_mb
        self.root = root

    def _run_file(self, directory: Path, filename: str) -> ExecutionResult:
        start = time.monotonic()
        preexec = _limit_resources(self.cpu_seconds, self.memory_mb) if resource else None
        try:
            completed = subprocess.run(
                [sys.executable, "-E", "-s", filename],
                cwd=str(directory),
                env=_restricted_environment(),
                capture_output=True,
                text=True,
                timeout=self.timeout,
                preexec_fn=preexec,
            )
            duration = time.monotonic() - start
            stdout, stderr, exit_code, timed_out = (
                completed.stdout,
                completed.stderr,
                completed.returncode,
                False,
            )
        except subprocess.TimeoutExpired as exc:
            duration = time.monotonic() - start
            stdout = exc.stdout or ""
            stderr = (exc.stderr or "") + "\nSANDBOX: cell exceeded timeout and was terminated"
            exit_code = None
            timed_out = True

        if isinstance(stdout, bytes):  # pragma: no cover - defensive
            stdout = stdout.decode("utf-8", "replace")
        if isinstance(stderr, bytes):  # pragma: no cover - defensive
            stderr = stderr.decode("utf-8", "replace")

        parsed = self._extract_result(stdout)
        success = (exit_code == 0) and not timed_out and parsed is not None
        return ExecutionResult(
            success=success,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=duration,
            timed_out=timed_out,
            result=parsed,
        )

    @staticmethod
    def _extract_result(stdout: str) -> Optional[Dict[str, Any]]:
        for line in reversed(stdout.splitlines()):
            if line.startswith(RESULT_MARKER):
                try:
                    return json.loads(line[len(RESULT_MARKER):])
                except json.JSONDecodeError:
                    return None
        return None

    def run_code(self, code: str, filename: str = "cell.py") -> ExecutionResult:
        """Run a standalone script with no harness; used for quick sanity checks."""
        with tempfile.TemporaryDirectory(prefix="sandbox-cell-", dir=self.root) as tmp:
            directory = Path(tmp)
            (directory / filename).write_text(code, encoding="utf-8")
            return self._run_file(directory, filename)

    def run_harness(self, candidate_code: str, harness_code: str) -> ExecutionResult:
        """Run candidate code against a generated test harness in one cell.

        The harness must ``import candidate`` and print a single line of the
        form ``SANDBOX_RESULT_JSON={"passed": N, "total": M, ...}``.
        """
        with tempfile.TemporaryDirectory(prefix="sandbox-cell-", dir=self.root) as tmp:
            directory = Path(tmp)
            (directory / "candidate.py").write_text(candidate_code, encoding="utf-8")
            (directory / "harness.py").write_text(harness_code, encoding="utf-8")
            return self._run_file(directory, "harness.py")

    @staticmethod
    def compiles(code: str) -> bool:
        """Cheap syntax gate so obviously broken mutations are discarded fast."""
        try:
            compile(code, "<mutant>", "exec")
            return True
        except SyntaxError:
            return False


def next_cell_id(counter: int) -> str:
    return f"cell-{counter:06d}"
