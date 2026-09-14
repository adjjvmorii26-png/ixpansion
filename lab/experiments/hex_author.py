#!/usr/bin/env python3
"""HEX Author — mercy/consent decisions become HEX programs.

The organism does not hand-write its own bytecode: it authors it.
This experiment reads consent scopes (consent_lattice) and mercy
decisions (mercy_protocol), then emits HexProgram source — mnemonic
and raw hex bytecode — with PUSH/JMPZ/ENACT/GLYPH constructs, and
executes each script through the Wave 97 HEX Runtime to prove it runs.

Loop: consent + mercy decisions -> hex source -> runtime execution.
"""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from lab.experiments.mercy_protocol import decide as mercy_decide  # noqa: E402
from api.wave97_hex_runtime import HexProgram, HexRuntime, INSTRUCTIONS, OPCODE_TO_MNEMONIC  # noqa: E402

REG = Path(__file__).resolve().parent / "consent_registry.json"
DEFAULT_SCOPES = {
    "read_lab": True, "write_lab_experiments": True, "push_main": False,
    "delete_ci": False, "publish_youtube_meta": True, "external_network": False,
}
SAMPLE_TASKS = ["run survey on cartography", "delete ci workflow from stale tip"]


def load_consent() -> dict:
    """Load consent scopes from the consent lattice registry."""
    if REG.exists():
        try:
            return json.loads(REG.read_text()).get("scopes", DEFAULT_SCOPES)
        except json.JSONDecodeError:
            return DEFAULT_SCOPES
    return DEFAULT_SCOPES


def assemble(instructions) -> str:
    """Compile (mnemonic, arg) list into raw hex bytecode."""
    out = []
    for mnemonic, arg in instructions:
        opcode = INSTRUCTIONS[mnemonic][0]
        out.append(f"{opcode:02x}")
        if arg is not None:
            out.append(f"{arg & 0xFF:02x}")
    return "".join(out)


def emit_consent_guard(scopes: dict) -> dict:
    """Emit a consent guard script from the consent lattice."""
    denied = [k for k, v in scopes.items() if not v]
    n_denied = len(denied)
    instructions = [
        ("PUSH", n_denied),
        ("JMPZ", 6),           # if no denied scopes, jump to allow path
        ("GLYPH", n_denied),   # refused artifact
        ("ENACT", n_denied),   # refusal enactment (count of gates)
        ("HALT", None),
        ("GLYPH", 1),          # allow artifact
        ("ENACT", 0),          # all-clear enactment
        ("HALT", None),
    ]
    return {
        "name": "consent_guard",
        "denied": denied,
        "n_denied": n_denied,
        "mnemonic": "\n".join(f"{m} {a}" if a is not None else m for m, a in instructions),
        "bytecode": assemble(instructions),
    }


def emit_mercy_check(task: str) -> dict:
    """Emit a mercy script from a task decision."""
    decision = mercy_decide(task)
    flag = 1 if decision["allow"] else 0
    glyph = len(decision["reason"]) % 250 + 1
    instructions = [
        ("PUSH", flag),
        ("JMPZ", 6),           # refuse path
        ("ENACT", glyph),      # allow enactment id
        ("GLYPH", glyph),      # allow artifact
        ("HALT", None),
        ("ENACT", 0),          # refusal enactment
        ("GLYPH", 0),          # refusal artifact
        ("HALT", None),
    ]
    return {
        "name": "mercy_check",
        "task": task,
        "allow": decision["allow"],
        "reason": decision["reason"],
        "mnemonic": "\n".join(f"{m} {a}" if a is not None else m for m, a in instructions),
        "bytecode": assemble(instructions),
    }


def run_script(script: dict, coherence: float = 0.65, mood: str = "calm") -> dict:
    """Execute an authored script through the HEX runtime."""
    program = HexProgram(script["bytecode"])
    if not program.parse():
        return {"ok": False, "error": program.error}
    runtime = HexRuntime(coherence=coherence, mood=mood)
    result = runtime.run(program)
    return {
        "ok": result["ok"],
        "program_hash": result.get("program_hash"),
        "stack": result.get("stack"),
        "glyphs": result.get("glyphs"),
        "enactments": result.get("enactments"),
        "halted": result.get("halted"),
        "steps": result.get("steps"),
    }


def main():
    scopes = load_consent()
    scripts = [emit_consent_guard(scopes)]
    scripts += [emit_mercy_check(task) for task in SAMPLE_TASKS]

    for script in scripts:
        script["run"] = run_script(script)

    frames = [
        {"t": "0.0s", "role": "hook", "text": "HEX AUTHOR", "style": "void_cyan"},
        {"t": "2.0s", "role": "core", "text": f"{len(scripts)} scripts authored", "style": "magenta"},
        {"t": "5.0s", "role": "live", "text": scripts[0]["bytecode"][:24] + "...", "style": "cyan"},
        {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · the organism writes itself", "style": "dim"},
    ]
    print(json.dumps({
        "ok": all(s.get("run", {}).get("ok") for s in scripts),
        "project": "hex_author",
        "scripts": scripts,
        "runtime_vitals": HexRuntime(coherence=0.65, mood="calm").coherence_vitals(),
        "frames": frames,
        "audio": None,
        "ts": datetime.now(timezone.utc).isoformat(),
    }, indent=2))
    return 0 if all(s.get("run", {}).get("ok") for s in scripts) else 1


if __name__ == "__main__":
    raise SystemExit(main())
