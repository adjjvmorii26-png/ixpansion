"""Wave 98 — HEX Cathedral Lacery.

Wave 97 gave the organism a runtime; Wave 98 gives it a body wall.
Programs no longer run alone — chapels (segments) declare altars
(labels), and any chapel can call across the aisle with JMPZ @altar.
The cathedral laces them into one flattened program, so the organism
executes its whole liturgy in a single breath.

Conventions inside a bundle source:
  ; #chapel NAME        begins a chapel (all following lines belong to it)
  ; #altar LABEL        exports the NEXT instruction as an altar
  JMPZ @LABEL           jumps to an altar in any chapel (cross-segment link)
  GLYPH 7               unchanged numeric glyphs still work

Builds upon:
- Wave 97: HEX Runtime (execution engine)
- Wave 96: HEX Grammar Evolution
- Wave 95: Ritual Governance (ENACT)
- Wave 93: HEX-Language Emergence
"""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from api.wave97_hex_runtime import HexProgram, HexRuntime, INSTRUCTIONS

DATA = Path(__file__).resolve().parents[1] / "data"
STATE_FILE = DATA / "wave98_hex_cathedral.json"
MAX_CHAPELS = 64

DEFAULT_BUNDLE = (
    "; ---- consent_program.hexsrc ----\n"
    "; #chapel consent_chapel\n"
    "PUSH 1\n"
    "PUSH 0\n"
    "ADD\n"
    "PUSH 0\n"
    "ADD\n"
    "PUSH 1\n"
    "ADD\n"
    "PUSH 0\n"
    "ADD\n"
    "PUSH 1\n"
    "ADD\n"
    "; #altar consent_hall\n"
    "GLYPH\n"
    "ENACT\n"
    "HALT\n"
    "\n"
    "; ---- mercy_program.hexsrc ----\n"
    "; #chapel mercy_chapel\n"
    "PUSH 0\n"
    "; #altar refuse_rite\n"
    "JMPZ @consent_hall\n"
    "PUSH 1\n"
    "ENACT\n"
    "HALT\n"
    "GLYPH\n"
    "HALT\n"
)


def _split_bundle(source: str) -> List[Tuple[str, List[str]]]:
    """Split bundle source into (segment_name, [lines]) by markers."""
    segments: List[Tuple[str, List[str]]] = []
    current_name: Optional[str] = None
    current: List[str] = []
    for ln in source.splitlines():
        stripped = ln.strip()
        if stripped.startswith("; ---- ") and stripped.endswith(" ----"):
            if current_name is not None and current:
                segments.append((current_name, current))
            current = []
            current_name = stripped.strip("; -").strip()
        else:
            current.append(ln)
    if current_name is not None and current:
        segments.append((current_name, current))
    return segments


def _instr_source(instrs: List[Tuple[str, Optional[int]]]) -> str:
    """Render a flattened instruction list back to source text for hashing."""
    lines: List[str] = []
    for mnemonic, arg in instrs:
        if arg is None:
            lines.append(mnemonic)
        else:
            lines.append(f"{mnemonic} {arg}")
    return "\n".join(lines)


class HexCathedral:
    """Laces chapels (hex segments) into one executable body."""

    def __init__(self) -> None:
        self.chapels: List[dict] = []
        self.altars: Dict[str, dict] = {}
        self.laces: List[dict] = []
        self.flattened: List[Tuple[str, Optional[int]]] = []
        self.program_hash: Optional[str] = None
        self.error: Optional[str] = None

    def lace(self, source: str) -> bool:
        """Parse a bundle, resolve @label refs, flatten into one program."""
        self.chapels = []
        self.altars = {}
        self.laces = []
        self.flattened = []
        self.error = None

        segments = _split_bundle(source)
        if not segments:
            self.error = "no chapels found in bundle"
            return False

        pending: List[Tuple[str, str, int]] = []  # (chapel, label, flat_idx)

        for name, lines in segments:
            chapel_name = name
            local_instrs: List[Tuple[str, Optional[int]]] = []
            arch: Dict[str, int] = {}  # label -> 1-based absolute line

            for ln in lines:
                stripped = ln.strip()
                if not stripped:
                    continue
                if stripped.startswith("; #chapel"):
                    parts = stripped.split()
                    if len(parts) >= 3:
                        chapel_name = parts[2]
                    continue
                if stripped.startswith("; #altar"):
                    parts = stripped.split()
                    if len(parts) >= 3:
                        label = parts[2]
                        if label in arch:
                            self.error = f"duplicate altar {label}"
                            return False
                        arch[label] = len(self.flattened) + len(local_instrs) + 1
                    continue
                if stripped.startswith(";"):
                    continue

                parts = stripped.split()
                mnemonic = parts[0].upper()
                if mnemonic not in INSTRUCTIONS:
                    self.error = f"unknown instruction {parts[0]}"
                    return False

                arg: Optional[int] = None
                if len(parts) > 1:
                    raw = parts[1]
                    if raw.startswith("@"):
                        if mnemonic != "JMPZ":
                            self.error = f"{mnemonic} cannot take an @altar label (JMPZ only)"
                            return False
                        idx = len(self.flattened) + len(local_instrs)
                        pending.append((chapel_name, raw[1:], idx))
                        local_instrs.append(("JMPZ", None))
                        continue
                    try:
                        arg = int(raw)
                    except ValueError:
                        self.error = f"instruction {mnemonic} needs an integer argument"
                        return False
                elif INSTRUCTIONS[mnemonic][1] > 0 and mnemonic not in ("GLYPH", "ENACT"):
                    self.error = f"instruction {mnemonic} needs an argument"
                    return False
                elif INSTRUCTIONS[mnemonic][1] > 0:
                    arg = 0

                local_instrs.append((mnemonic, arg))

            start = len(self.flattened)
            self.flattened.extend(local_instrs)
            self.chapels.append({
                "name": chapel_name,
                "segment": name,
                "line_start": start + 1,
                "line_end": len(self.flattened),
                "instructions": len(local_instrs),
            })
            for label, line in arch.items():
                if label in self.altars:
                    self.error = f"duplicate altar {label}"
                    return False
                self.altars[label] = {"chapel": chapel_name, "line": line}

        for chapel_name, label, idx in pending:
            altar = self.altars.get(label)
            if altar is None:
                self.error = f"chapel {chapel_name} calls unknown altar @{label}"
                return False
            self.flattened[idx] = ("JMPZ", altar["line"])
            self.laces.append({
                "from": chapel_name,
                "to": altar["chapel"],
                "label": label,
                "target_line": altar["line"],
            })

        self.program_hash = hashlib.sha256(source.encode()).hexdigest()[:16]
        return True

    def program(self) -> HexProgram:
        """Materialize the flattened instruction list as a runnable program."""
        prog = HexProgram(_instr_source(self.flattened))
        prog.instructions = list(self.flattened)
        if not prog.program_hash:
            prog.program_hash = self.program_hash or hashlib.sha256(prog.source.encode()).hexdigest()[:16]
        return prog

    def run(self, runtime: Optional[HexRuntime] = None, coherence: float = 0.75,
            mood: str = "chaotic") -> Dict[str, Any]:
        """Execute the laced cathedral through the Wave 97 runtime."""
        prog = self.program()
        rt = runtime or HexRuntime(coherence=coherence, mood=mood)
        result = rt.run(prog)

        heat: Dict[str, int] = {}
        for entry in result.get("trace", []):
            idx = entry.get("pc")
            if idx is not None and 0 <= idx < len(self.flattened):
                for ch in self.chapels:
                    if ch["line_start"] - 1 <= idx < ch["line_end"]:
                        heat[ch["name"]] = heat.get(ch["name"], 0) + 1
                        break
        result["chapel_heat"] = heat
        result["laces"] = self.laces
        return result


def _load() -> Tuple[HexCathedral, dict]:
    """Load cathedral state from living state file."""
    cathedral = HexCathedral()
    state: dict = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            state = {}
    bundle = state.get("bundle", "") or DEFAULT_BUNDLE
    cathedral.lace(bundle)
    if cathedral.error or not cathedral.laces:
        # Stale or incompatible bundle: relace with default to keep laces alive
        cathedral.lace(DEFAULT_BUNDLE)
    return cathedral, state


def _save(cathedral: HexCathedral, state: dict) -> None:
    """Persist cathedral state."""
    data = {
        "bundle": state.get("bundle", DEFAULT_BUNDLE),
        "heat": state.get("heat", {}),
        "history": state.get("history", [])[-20:],
    }
    STATE_FILE.write_text(json.dumps(data, indent=2))


def handler(req: dict) -> dict:
    """Wave 98 handler: hex cathedral lacing."""
    action = req.get("action", "status")
    cathedral, state = _load()

    if action == "status":
        return {
            "action": "status",
            "wave": 98,
            "chapels": len(cathedral.chapels),
            "altars": len(cathedral.altars),
            "laces": len(cathedral.laces),
            "flattened_instructions": len(cathedral.flattened),
            "heat": state.get("heat", {}),
            "message": "HEX cathedral status",
        }

    if action == "lace":
        bundle = req.get("bundle", state.get("bundle", "")) or DEFAULT_BUNDLE
        if not cathedral.lace(bundle):
            return {"ok": False, "error": cathedral.error, "action": "lace"}
        state["bundle"] = bundle
        _save(cathedral, state)
        return {
            "action": "lace",
            "wave": 98,
            "chapels": [c["name"] for c in cathedral.chapels],
            "altars": cathedral.altars,
            "laces": cathedral.laces,
            "flattened_instructions": len(cathedral.flattened),
            "program_hash": cathedral.program_hash,
            "message": "Cathedral laced",
        }

    if action == "run":
        bundle = req.get("bundle", state.get("bundle", ""))
        if bundle:
            cathedral.lace(bundle)
        result = cathedral.run(coherence=float(req.get("coherence", 0.75)),
                               mood=req.get("mood", "chaotic"))
        heat = state.get("heat", {})
        for ch, steps in result.get("chapel_heat", {}).items():
            heat[ch] = heat.get(ch, 0) + steps
        history = state.setdefault("history", [])
        history.append({
            "ts": time.time(),
            "program_hash": cathedral.program_hash,
            "steps": result.get("steps", 0),
            "glyphs": len(result.get("glyphs", [])),
            "halted": result.get("halted"),
        })
        state["heat"] = heat
        _save(cathedral, state)
        return {
            "action": "run",
            "wave": 98,
            "program": cathedral.program().to_dict(),
            "result": result,
            "message": "Cathedral run complete",
        }

    if action == "reset":
        state.clear()
        state["bundle"] = DEFAULT_BUNDLE
        _save(cathedral, state)
        return {"action": "reset", "wave": 98, "message": "Cathedral reset"}

    if action == "history":
        return {"action": "history", "wave": 98, "history": state.get("history", [])}

    return {"ok": False, "error": f"Unknown action: {action}"}


def coherence_vitals() -> dict:
    """Wave 98 vitals."""
    cathedral, _ = _load()
    return {
        "wave": 98,
        "instruction_count": len(INSTRUCTIONS),
        "chapels": len(cathedral.chapels),
        "altars": len(cathedral.altars),
        "laces": len(cathedral.laces),
        "flattened_instructions": len(cathedral.flattened),
    }


def resonates_with() -> List[str]:
    return ["wave97_hex_runtime", "wave95_ritual_governance", "wave96_hex_grammar_evolution"]
