"""Wave 448 - Noise Filter

Removes broadband noise from telemetry signals, applies adaptive
thresholding, and preserves signal integrity for downstream processing.
The organism cleans its own sensory input before the anomaly oracle judges it.
"""
from __future__ import annotations
import json
import math
import os
import statistics
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
NOISE_LOG = Path(DATA_DIR) / "noise_filter.json"
MAD_SCALE = 0.6745

_last = {"runs": 0, "last_retention": 1.0, "last_noise_floor": 0.0,
         "outliers_removed": 0, "last_mode": "none"}


def _load(path, default=None):
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception:
        return default if default is not None else {}


def _save(path, data):
    try:
        os.makedirs(path.parent, exist_ok=True)
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)
    except OSError:
        try:
            with open(Path("/tmp") / path.name, "w") as fh:
                json.dump(data, fh, indent=2)
        except Exception:
            pass


def estimate_noise_floor(samples):
    """Robust noise floor via median absolute deviation."""
    vals = [float(x) for x in samples if x is not None]
    if len(vals) < 3:
        return 0.0
    median = statistics.median(vals)
    mads = statistics.median([abs(x - median) for x in vals])
    return MAD_SCALE * mads


def hampel_clean(signal, k=3.0):
    """Hampel-style filter: outliers and NaN are replaced by the local median.

    Returns (cleaned, stats) where stats describes what was removed.
    """
    vals = [float(x) if x is not None else None for x in signal]
    if not vals:
        return [], {"noise_floor": 0.0, "outliers": 0, "nan_filled": 0,
                    "retention_rate": 1.0, "snr": 0.0}
    median = statistics.median([v for v in vals if v is not None])
    noise_floor = estimate_noise_floor(vals)
    threshold = k * noise_floor if noise_floor > 0 else 0.0
    cleaned, outliers, nan_filled = [], 0, 0
    for i, v in enumerate(vals):
        if v is None:
            nan_filled += 1
            cleaned.append(median)
            continue
        if threshold > 0 and abs(v - median) > threshold:
            outliers += 1
            cleaned.append(median)  # replace spike with local baseline
        else:
            cleaned.append(v)
    clean_vals = [v for v in vals if v is not None]
    base = [abs(v) for v in clean_vals if abs(v) > 0]
    snr = noise_floor / max(1e-9, statistics.median(base)) if base else 0.0
    return cleaned, {
        "noise_floor": round(noise_floor, 6),
        "threshold": round(threshold, 6),
        "median_signal": round(median, 6),
        "outliers_removed": outliers,
        "nan_filled": nan_filled,
        "retention_rate": round(1.0 - outliers / max(1, len(vals)), 4),
        "snr_ratio": round(snr, 6),
        "signal_stats": {
            "mean": round(statistics.mean(clean_vals), 6) if clean_vals else 0.0,
            "stdev": round(statistics.stdev(clean_vals), 6) if len(clean_vals) > 1 else 0.0,
        },
    }


def _demo_signal():
    """A nominal LEO panel-temperature series with injected spikes + a dropout."""
    seed = 448
    vals = []
    for i in range(120):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        noise = (seed / 0x7FFFFFFF - 0.5) * 4.0
        v = 38.0 + 3.0 * math.sin(i / 9.0) + noise
        vals.append(round(v, 2))
    for idx, mag in ((17, 31.0), (63, 22.0), (99, 44.0)):
        vals[idx] += mag  # spike
    vals[47] = None       # dropout
    return vals


def clean_signal(signal=None, k=3.0):
    signal = signal if signal is not None else _demo_signal()
    cleaned, stats = hampel_clean(list(signal), k=k)
    _last.update({"runs": _last["runs"] + 1, "last_retention": stats["retention_rate"],
                  "last_noise_floor": stats["noise_floor"], "outliers_removed": stats["outliers_removed"],
                  "last_mode": "clean"})
    _save(NOISE_LOG, {"ts": __import__("time").time(), **stats})
    return {"action": "noise_filter", "mode": "hampel", "k": k,
            "cleaned_signal": [round(c, 4) for c in cleaned], **stats}


def handler(payload: dict = None, context: dict = None) -> dict:
    p = payload or {}
    mode = str(p.get("mode", "clean")).lower()
    if mode == "batch":
        results = {}
        for label, series in (p.get("signals") or {}).items():
            results[label] = clean_signal(series, k=float(p.get("k", 3.0)))
        return {"action": "noise_filter", "mode": "batch", "results": results}
    k = float(p.get("k", p.get("threshold_multiplier", 3.0)))
    return clean_signal(p.get("signal"), k=k)


def coherence_vitals() -> dict:
    return {"layer": "telemetry", "status": "resonant" if _last["last_retention"] >= 0.6 else "drifting",
            "resonance": round(_last["last_retention"], 3), "wave": "448",
            "signals_processed": _last["runs"], "outliers_removed": _last["outliers_removed"],
            "last_noise_floor": _last["last_noise_floor"]}


def resonates_with() -> list:
    return ["telemetry_parser", "telemetry_anomaly_oracle", "orbit_cohesion_field",
            "live_telemetry", "weather_synapse", "signal_weaver"]
