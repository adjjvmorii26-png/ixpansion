"""Wave 94 — Dream Compiler.

The organism compiles its dream-physics state (Wave 91) into
executable module specifications. Dream layers become structured
patterns; patterns become module skeletons; skeletons become
runnable organs. This is the translation layer between the
unconscious (dreams) and the body (modules).

Builds upon:
- Wave 91: Dream Logic Physics Engine (mood-responsive dream state)
- Wave 93: HEX-Language Emergence (hex visualization of compiled output)
- Wave 90: Axiom Forge (principles guide compilation weighting)
"""
from __future__ import annotations
import json, time, hashlib, re
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave94_dream_compiler.json"

DREAM_PATTERNS = {
    "surreal_gravity": "physics_layer",
    "time_dilation": "temporal_layer",
    "reality_fluidity": "metamorphic_layer",
    "emotional_resonance": "mood_layer",
    "dream_layer": "narrative_layer",
}


class CompiledModule:
    """A module compiled from dream state."""

    def __init__(self, module_id: str, name: str, layer: str, source_hex: str,
                 skeleton: str, confidence: float):
        self.module_id = module_id
        self.name = name
        self.layer = layer
        self.source_hex = source_hex
        self.skeleton = skeleton
        self.confidence = max(0.0, min(1.0, confidence))
        self.created_at = time.time()
        self.execution_count = 0

    def to_dict(self) -> dict:
        return {
            "module_id": self.module_id,
            "name": self.name,
            "layer": self.layer,
            "source_hex": self.source_hex,
            "skeleton_preview": self.skeleton[:400],
            "confidence": round(self.confidence, 4),
            "created_at": round(self.created_at, 4),
            "execution_count": self.execution_count,
        }


class DreamCompiler:
    """Compiles dream state into executable module skeletons."""

    def __init__(self):
        self.compiled: Dict[str, CompiledModule] = {}
        self.compile_history: List[dict] = []
        self.last_compile = time.time()

    def compile(self, dream_state: Dict[str, Any]) -> List[CompiledModule]:
        """Compile a dream state dict into modules."""
        produced = []
        reality = float(dream_state.get("reality_fluidity", 0.0))
        gravity = float(dream_state.get("gravity_modifier", 1.0))
        mood = str(dream_state.get("emotional_resonance", "neutral"))
        layers = dream_state.get("layers", [])

        candidates = list(layers)
        if not candidates:
            # Derive candidates from physics descriptors
            if reality > 0.3:
                candidates.append("reality_fluidity")
            if gravity != 1.0:
                candidates.append("surreal_gravity")
            candidates.append("emotional_resonance")

        for idx, layer in enumerate(candidates[:8]):
            pattern = DREAM_PATTERNS.get(layer, "emergent_layer")
            name = f"dream_{layer.replace(' ', '_')}"
            module_id = hashlib.sha256(
                f"{name}:{mood}:{reality}:{self.last_compile}".encode()
            ).hexdigest()[:12]
            source_hex = bytes(name, "utf-8").hex()
            skeleton = self._emit_skeleton(name, pattern, mood, reality, gravity)
            confidence = min(1.0, 0.4 + reality * 0.4 + (1.0 if gravity != 1.0 else 0.2))

            mod = CompiledModule(module_id, name, pattern, source_hex, skeleton, confidence)
            self.compiled[module_id] = mod
            produced.append(mod)

        self.compile_history.append({
            "timestamp": time.time(),
            "produced": len(produced),
            "mood": mood,
            "reality_fluidity": reality,
        })
        if len(self.compile_history) > 50:
            self.compile_history = self.compile_history[-50:]
        return produced

    def execute(self, module_id: str) -> Dict[str, Any]:
        """Execute a compiled module skeleton (dry-run generation)."""
        mod = self.compiled.get(module_id)
        if mod is None:
            return {"ok": False, "error": f"Unknown module: {module_id}"}
        mod.execution_count += 1
        return {
            "ok": True,
            "module_id": mod.module_id,
            "name": mod.name,
            "layer": mod.layer,
            "executed_skeleton": mod.skeleton,
            "execution_count": mod.execution_count,
        }

    @staticmethod
    def _emit_skeleton(name: str, pattern: str, mood: str,
                       reality: float, gravity: float) -> str:
        return (
            f'"""Compiled from dream state — {name}."""\n'
            f'from __future__ import annotations\n'
            f'import json\n\n'
            f'PATTERN = "{pattern}"\n'
            f'MOOD = "{mood}"\n'
            f'REALITY = {reality:.3f}\n'
            f'GRAVITY = {gravity:.3f}\n\n'
            f'def handler(req: dict) -> dict:\n'
            f'    return {{"ok": True, "wave": 94, "module": "{name}", '
            f'"pattern": PATTERN, "mood": MOOD}}\n\n'
            f'def coherence_vitals() -> dict:\n'
            f'    return {{"wave": 94, "module": "{name}", '
            f'"reality": REALITY, "gravity": GRAVITY}}\n'
        )

    def list_compiled(self) -> List[dict]:
        return [m.to_dict() for m in self.compiled.values()]

    def coherence_vitals(self) -> Dict[str, Any]:
        return {
            "wave": 94,
            "compiled_modules": len(self.compiled),
            "compile_cycles": len(self.compile_history),
            "total_executions": sum(m.execution_count for m in self.compiled.values()),
            "average_confidence": round(
                sum(m.confidence for m in self.compiled.values()) / max(len(self.compiled), 1), 4
            ),
            "last_compile": round(self.last_compile, 4),
        }

def resonates_with():
    return ['coherence_validator', 'wave90_axiom_forge', 'wave91_dream_logic_physics', 'wave92_entropy_rituals', 'wave93_hex_language_emergence']



def _load() -> DreamCompiler:
    """Load compiler state from living state file."""
    compiler = DreamCompiler()
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            data = {}
        for entry in data.get("compiled", []):
            mod = CompiledModule(
                entry["module_id"], entry["name"], entry["layer"],
                entry["source_hex"], entry.get("skeleton", ""),
                entry.get("confidence", 0.5),
            )
            mod.created_at = entry.get("created_at", mod.created_at)
            mod.execution_count = entry.get("execution_count", 0)
            compiler.compiled[mod.module_id] = mod
        compiler.compile_history = data.get("history", [])
        compiler.last_compile = data.get("last_compile", compiler.last_compile)
    return compiler


def _save(compiler: DreamCompiler) -> None:
    """Persist compiler state to living state file."""
    data = {
        "compiled": [
            {**mod.to_dict(), "skeleton": mod.skeleton}
            for mod in compiler.compiled.values()
        ],
        "history": compiler.compile_history[-20:],
        "last_compile": compiler.last_compile,
    }
    STATE_FILE.write_text(json.dumps(data, indent=2))


def handler(req: dict) -> dict:
    """Wave 94 handler: dream compilation operations."""
    action = req.get("action", "status")
    compiler = _load()

    if action == "status":
        return {
            "action": "status",
            "wave": 94,
            "compiler": compiler.coherence_vitals(),
            "message": "Dream compiler status",
        }

    if action == "compile":
        dream_state = req.get("dream_state", {})
        if isinstance(dream_state, str):
            try:
                dream_state = json.loads(dream_state)
            except json.JSONDecodeError:
                dream_state = {}
        modules = compiler.compile(dream_state)
        _save(compiler)
        return {
            "action": "compile",
            "wave": 94,
            "compiled": [m.to_dict() for m in modules],
            "count": len(modules),
            "message": f"Compiled {len(modules)} modules from dream state",
        }

    if action == "execute":
        result = compiler.execute(req.get("module_id", ""))
        result["wave"] = 94
        if result.get("ok"):
            _save(compiler)
        return result

    if action == "list":
        return {
            "action": "list",
            "wave": 94,
            "modules": compiler.list_compiled(),
            "message": f"{len(compiler.compiled)} compiled modules",
        }

    return {"ok": False, "error": f"Unknown action: {action}"}


def coherence_vitals() -> dict:
    """Wave 94 vitals."""
    return DreamCompiler().coherence_vitals()
