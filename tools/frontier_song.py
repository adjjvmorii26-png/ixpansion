"""Frontier Song — sonification of the module constellation.

Turns every module name into a musical note via content-hash mapping:
each snake_case token becomes a pitch, duration, and velocity, and the
result is a short deterministic melody rendered as a WAV file.

    python tools/frontier_song.py                          # default
    python tools/frontier_song.py --output song.wav --dur 8
    python tools/frontier_song.py --json                   # note seq

Pure stdlib — no external audio dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import wave
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"

# A pentatonic-ish scale in Hz (2 octaves, C3-B5)
_SCALE = [
    130.81, 146.83, 164.81, 196.00, 220.00,
    261.63, 293.66, 329.63, 392.00, 440.00,
    523.25, 587.33, 659.26, 783.99, 880.00,
    1046.50, 1174.66, 1318.51, 1567.98, 1760.00,
]


def module_names() -> List[str]:
    if not API_DIR.exists():
        return []
    return sorted(p.stem for p in API_DIR.glob("*.py")
                  if p.stem not in ("__init__", "index", "unified_router"))


def _hash_int(name: str, index: int) -> int:
    h = hashlib.sha256(f"{name}::{index}".encode()).hexdigest()
    return int(h[:8], 16)


def name_to_note(name: str, index: int) -> Tuple[float, float, float]:
    """Map a module name to (frequency_hz, duration_s, velocity 0..1)."""
    h = _hash_int(name, index)
    freq = _SCALE[h % len(_SCALE)]
    # vary by octave shift from the name's character entropy
    entropy_bonus = sum(ord(c) for c in name) % 12
    freq *= 2 ** ((entropy_bonus % 12 - 6) / 12)
    freq = min(freq, 1760.0)
    duration = 0.04 + (h % 800) / 10000.0
    velocity = 0.4 + (h % 400) / 1000.0
    return freq, min(duration, 0.3), min(velocity, 1.0)


def _sine(freq: float, t: float, velocity: float) -> float:
    """Simple sine wave with soft attack."""
    import math
    return velocity * math.sin(2 * math.pi * freq * t)


def generate_notes(names: List[str]) -> List[Dict[str, Any]]:
    return [{"name": n, "freq": round(f, 2), "dur": round(d, 3), "vel": round(v, 3)}
            for i, n in enumerate(names)
            for f, d, v in [name_to_note(n, i)]]


def render_wav(names: List[str], sample_rate: int = 8000, bit_depth: int = 8,
               output: Path | None = None) -> Path:
    """Render the module constellation as a WAV file."""
    notes = generate_notes(names)
    total_dur = sum(n["dur"] for n in notes)
    total_samples = int(total_dur * sample_rate)
    if total_samples == 0:
        total_samples = sample_rate  # at least 1s of silence

    samples = bytearray()
    t = 0.0
    for note in notes:
        n_samples = int(note["dur"] * sample_rate)
        attack = min(0.05, note["dur"] * 0.3)
        for i in range(n_samples):
            t_local = i / sample_rate
            env = min(t_local / attack, 1.0) if attack > 0 else 1.0
            val = _sine(note["freq"], t, note["vel"] * env)
            # 8-bit unsigned PCM: 128 ± range
            sample = max(0, min(255, int(128 + val * 100)))
            samples.append(sample)
            t += 1.0 / sample_rate

    if output is None:
        output = ROOT / "tools" / "frontier_song.wav"

    with wave.open(str(output), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(bit_depth // 8)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(samples))

    return output


def main() -> None:
    ap = argparse.ArgumentParser(description="Sonify the frontier")
    ap.add_argument("--output", "-o", help="output WAV path")
    ap.add_argument("--json", dest="as_json", action="store_true",
                    help="print note sequence as JSON instead of rendering audio")
    ap.add_argument("--names", type=str, help="comma-separated names to sonify (overrides api scan)")
    args = ap.parse_args()

    names = module_names()
    if args.names:
        names = [n.strip() for n in args.names.split(",") if n.strip()]

    if args.as_json:
        print(json.dumps(generate_notes(names), indent=2))
        return

    out = render_wav(names, output=Path(args.output) if args.output else None)
    import os
    size_kb = os.path.getsize(out) / 1024
    print(f"frontier_song.wav rendered: {len(names)} notes, {size_kb:.0f}KB, path={out}")


if __name__ == "__main__":
    main()
