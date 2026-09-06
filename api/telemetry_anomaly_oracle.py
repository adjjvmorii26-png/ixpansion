"""Wave 448 - Telemetry Anomaly Oracle

Looks at a telemetry stream and names what is wrong with it: corruption,
sensor drift, or a signal so clean it may be a spoof. Every value a satellite
reports is a small confession; the oracle reads between the samples.
"""
from __future__ import annotations
import json
import math
import statistics
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
ANOMALY_LOG = Path(DATA_DIR) / "telemetry_anomaly_oracle.json"


def examine(values, label="UNKNOWN", expected_range=None, timestamps=None):
    """Score a telemetry series across three anomaly families."""
    vals = [float(v) for v in values if v is not None]
    n = len(vals)
    if n < 4:
        return {"label": label, "verdict": "insufficient_data", "confidence": 0.0,
                "scores": {"corruption": 0.0, "drift": 0.0, "spoof": 0.0}, "n": n}
    median = statistics.median(vals)
    mad = statistics.median([abs(v - median) for v in vals]) * 1.4826
    mad = mad if mad > 0 else (statistics.pstdev(vals) or 1e-9)
    stdev = statistics.pstdev(vals) or 1e-9

    # Corruption: spikes beyond 5 MAD, or values outside the expected envelope.
    spikes = sum(1 for v in vals if abs(v - median) > 5.0 * mad)
    out_of_range = 0
    if expected_range:
        lo, hi = float(expected_range[0]), float(expected_range[1])
        out_of_range = sum(1 for v in vals if v < lo or v > hi)
    corruption = min(1.0, (spikes * 3.0 + out_of_range * 2.0) / n)

    # Drift: a linear trend that survives noise (CUSUM of deviations vs window).
    mu = statistics.mean(vals)
    run = 0.0
    max_run = 0.0
    for v in vals:
        run = max(0.0, run + (v - mu) / stdev)
        max_run = max(max_run, run)
    drift = min(1.0, max_run / (math.sqrt(n) * 1.4))

    # Spoof: unnaturally still signal with no jitter, or timestamps that are
    # too perfectly regular, or impossibly integer-heavy telemetry.
    quantized = sum(1 for v in vals if abs(v - round(v)) < 1e-9) / n
    jitter = stdev / (abs(mu) + 1e-9)
    ts_regular = 0.0
    if timestamps and len(timestamps) > 2:
        gaps = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
        if all(g > 0 for g in gaps):
            gap_stdev = statistics.pstdev(gaps)
            ts_regular = 1.0 if gap_stdev / (statistics.mean(gaps) + 1e-9) < 0.001 else 0.0
    spoof = min(1.0, quantized * 1.2 + (0.8 if jitter < 0.004 else 0.0) + ts_regular * 0.5)

    scores = {"corruption": round(corruption, 3), "drift": round(drift, 3),
              "spoof": round(spoof, 3)}
    worst = max(scores, key=scores.get)
    if scores[worst] < 0.18:
        verdict, confidence = "clean", round(1.0 - scores[worst], 3)
    elif worst == "corruption":
        verdict = "corrupted" if corruption >= 0.5 else "noisy"
        confidence = round(corruption, 3)
    elif worst == "drift":
        verdict = "sensor_drift" if drift >= 0.5 else "slight_drift"
        confidence = round(drift, 3)
    else:
        verdict = "possible_spoof" if spoof >= 0.5 else "suspiciously_clean"
        confidence = round(spoof, 3)
    return {"label": label, "verdict": verdict, "confidence": confidence,
            "scores": scores, "n": n, "mean": round(mu, 4),
            "stdev": round(stdev, 4), "signature": f"{label}:{verdict}"}


def _demo(payload):
    """Build demo streams: one corrupted, one drifting, one suspiciously clean."""
    seed = 448
    def gen():
        nonlocal seed
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        return seed / 0x7FFFFFFF
    streams = {}
    corrupted = [38.0 + (gen() - 0.5) * 4.0 for _ in range(80)]
    for i in (9, 21, 44, 62):
        corrupted[i] += 26.0 + gen() * 12.0
    streams["CORRUPTED-PANEL"] = corrupted
    drifting, base = [], 36.0
    for i in range(80):
        drifting.append(round(base + i * 0.06 + (gen() - 0.5) * 1.6, 3))
    streams["DRIFTING-CURRENT"] = drifting
    streams["SUSPICIOUS-TEMP"] = [36.40 + 0.01 * math.sin(i / 5.0) for i in range(80)]
    return {k: examine(v, label=k) for k, v in streams.items()}


def handler(payload: dict = None, context: dict = None) -> dict:
    p = payload or {}
    mode = str(p.get("mode", "examine")).lower()
    if mode in ("demo", "trials"):
        results = _demo(p)
    else:
        values = p.get("values") or p.get("signal")
        if not values:
            results = _demo(p)
        else:
            results = {"assessment": examine(
                values, label=str(p.get("label", "UNKNOWN")),
                expected_range=p.get("range"), timestamps=p.get("timestamps"))}
    try:
        with open(ANOMALY_LOG, "w") as fh:
            json.dump({"ts": time.time(), "results": results}, fh, indent=2)
    except OSError:
        try:
            with open("/tmp/telemetry_anomaly_oracle.json", "w") as fh:
                json.dump({"ts": time.time(), "results": results}, fh, indent=2)
        except Exception:
            pass
    return {"action": "telemetry_anomaly_oracle", "mode": mode, **results}


def coherence_vitals() -> dict:
    return {"layer": "telemetry", "status": "resonant", "resonance": 0.88, "wave": "448",
            "families": ["corruption", "drift", "spoof"], "last_verdict": "watchful"}


def resonates_with() -> list:
    return ["noise_filter", "telemetry_parser", "orbit_cohesion_field", "integrity_oracle",
            "anomaly_detector", "solar_weather_coupler", "orbital_storyteller"]
