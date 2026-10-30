#!/usr/bin/env python3
"""Runtime-neutral local test chamber.

Executes trusted Python or Node.js files without a shell and emits JSON evidence.
This is not a security sandbox; use a disposable OS/container boundary for untrusted code.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


MAX_CAPTURE_BYTES = 64 * 1024
RUNTIMES: dict[str, Callable[[str, str], list[str]]] = {
    "python": lambda executable, target: [executable, target],
    "node": lambda executable, target: [executable, target],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--runtime", choices=sorted(RUNTIMES), required=True)
    parser.add_argument("--target", required=True, help="Target file relative to project root")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--expect-exit", type=int, required=True)
    parser.add_argument("--expect-stdout", action="append", default=[])
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args(argv)
    if not 0.1 <= args.timeout <= 300:
        parser.error("--timeout must be between 0.1 and 300 seconds")
    if not -255 <= args.expect_exit <= 255:
        parser.error("--expect-exit must be between -255 and 255")
    return args


def resolve_target(root_arg: str, target_arg: str) -> tuple[Path, Path]:
    root = Path(root_arg).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be a directory")
    candidate = (root / target_arg).resolve(strict=True)
    if not candidate.is_file() or not candidate.is_relative_to(root):
        raise ValueError("Target must be an existing file inside the project root")
    return root, candidate


def build_environment() -> dict[str, str]:
    allowed = ("PATH", "HOME", "TMPDIR", "TEMP", "TMP", "SYSTEMROOT", "WINDIR")
    return {key: value for key, value in os.environ.items() if key in allowed}


def read_excerpt(data: bytes) -> str:
    clipped = data[:MAX_CAPTURE_BYTES]
    text = clipped.decode("utf-8", errors="replace")
    if len(data) > MAX_CAPTURE_BYTES:
        text += "\n[output truncated at 65536 bytes]"
    return text


def execute(args: argparse.Namespace) -> dict:
    started_at = utc_now()
    started = time.monotonic()
    root, target = resolve_target(args.root, args.target)
    executable = sys.executable if args.runtime == "python" else shutil.which("node")
    if not executable:
        raise FileNotFoundError(f"Runtime not found: {args.runtime}")
    command = RUNTIMES[args.runtime](executable, str(target))
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            env=build_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=args.timeout,
            check=False,
            shell=False,
        )
        exit_code = completed.returncode
        stdout = read_excerpt(completed.stdout)
        stderr = read_excerpt(completed.stderr)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = None
        stdout = read_excerpt(exc.stdout or b"")
        stderr = read_excerpt(exc.stderr or b"")
    assertions = [
        {"kind": "exit_code", "expected": args.expect_exit, "actual": exit_code,
         "passed": exit_code == args.expect_exit and not timed_out}
    ]
    assertions.extend(
        {"kind": "stdout_contains", "expected": expected, "passed": expected in stdout}
        for expected in args.expect_stdout
    )
    passed = all(item["passed"] for item in assertions)
    report = {
        "schema_version": "1.0",
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_ms": round((time.monotonic() - started) * 1000, 3),
        "project_root": str(root),
        "target": str(target.relative_to(root)),
        "runtime": args.runtime,
        "command": command,
        "timeout_seconds": args.timeout,
        "timed_out": timed_out,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "assertions": assertions,
        "result": "PASS" if passed else "FAIL",
    }
    if args.report:
        report_path = (root / args.report).resolve()
        if not report_path.is_relative_to(root):
            raise ValueError("Report path must remain inside project root")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        report["report_path"] = str(report_path.relative_to(root))
    return report


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        report = execute(args)
    except (ValueError, FileNotFoundError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"result": "BLOCKED", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
