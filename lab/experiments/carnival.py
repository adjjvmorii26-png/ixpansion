"""Lab Carnival — Dream residue, eclipse, haiku, ghosts, chrono seed, ink.

Additive only sync from main@7879dff. No wholesale branch merges.
"""
from __future__ import annotations

import json, time, math
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "carnival_state.json"


def dream_residue(coherence: float = 0.5) -> dict:
    """Generate a dream residue from current coherence state."""
    return {
        "residue": f"echo_{int(coherence * 100):03d}",
        "strength": round(coherence, 3),
        "timestamp": time.time(),
    }


def eclipse_signature(modules: int = 6) -> dict:
    """Calculate eclipse signature based on module count."""
    phases = [math.sin(t / 6.0 + i) for i, t in enumerate(range(modules))]
    return {
        "eclipse": "total" if sum(abs(p) for p in phases) > 4 else "partial",
        "phases": len(phases),
        "signature": "".join(f"{int(p):x}" for p in phases),
    }


def haiku_from_state(coherence: float, modules: int) -> dict:
    """Derive a haiku from organism state."""
    syllables = ["moon", "shadow", "whisper", "echo", "dream", "void"]
    return {
        "haiku": f"{syllables[int(coherence*5)%6]} {syllables[int(modules%6)]} {syllables[int(time.time())%6]}",
        "coherence": round(coherence, 3),
        "modules": modules,
    }


def chrono_seed() -> dict:
    """Generate a chrono seed for organism growth."""
    return {
        "seed": f"chrono_{int(time.time()) % 10000:04d}",
        "epoch": int(time.time()) // 3600,
        "height": int(math.sqrt(time.time()) % 50 + 10),
    }


def ink_blot(pattern: str = "default") -> dict:
    """Create an ink blot pattern."""
    return {
        "pattern": pattern,
        "blots": int(math.e ** (0.01 * time.time() % 10)),
        "timestamp": time.time(),
    }


def carnival_state() -> dict:
    """Return current carnival state."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"residues": [], "eclipses": [], "haikus": [], "seeds": [], "blots": []}


def _save_state(state: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def record_residue(coherence: float = 0.5) -> None:
    """Record a dream residue."""
    state = carnival_state()
    state["residues"].append(dream_residue(coherence))
    if len(state["residues"]) > 50:
        state["residues"] = state["residues"][-50:]
    _save_state(state)


record_residue(0.75)
print("Carnival module loaded — additive sync ready")
