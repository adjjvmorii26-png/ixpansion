"""Wave 437 — Temporal Resonance Map

Maps the temporal signature of the entire organism: which waves ripple longest,
which modules are most time-dense, where temporal clusters form. Creates a
"temporal heatmap" that reveals the organism's rhythm — not just what exists,
but when it breathes.
"""
from __future__ import annotations
import json, time, os, math
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MAP_LOG = os.path.join(DATA_DIR, "temporal_resonance_map.json")
API_DIR = os.path.dirname(__file__)


def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return d or {}

def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except Exception:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)


def _scan_module_timestamps():
    """Scan all api/*.py files for modification timestamps and wave-number patterns."""
    import re
    modules = []
    api_path = Path(API_DIR)
    for f in api_path.glob("*.py"):
        if f.name.startswith("__"): continue
        stat = f.stat()
        try:
            content = f.read_text(errors="ignore")[:2000]
            wave_match = re.search(r'[Ww]ave\s+(\d+)', content)
            wave = int(wave_match.group(1)) if wave_match else 0
        except Exception:
            wave = 0
        modules.append({
            "module": f.stem,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "wave": wave,
            "size": stat.st_size,
        })
    return modules


def _compute_temporal_clusters(modules, num_buckets=12):
    """Bucket modules by wave number to find temporal clusters."""
    if not modules: return []
    waves = [m["wave"] for m in modules if m["wave"] > 0]
    if not waves: return []

    min_w, max_w = min(waves), max(waves)
    if min_w == max_w:
        return [{"wave_range": f"{min_w}-{min_w}", "count": len(waves), "density": 1.0}]

    step = max(1, (max_w - min_w) // num_buckets)
    clusters = []
    for i in range(min_w, max_w + 1, step):
        end = min(i + step, max_w)
        count = sum(1 for w in waves if i <= w < end)
        density = round(count / max(1, step), 3)
        clusters.append({
            "wave_range": f"{i}-{end}",
            "count": count,
            "density": density,
            "pulse_strength": round(density * math.log2(count + 1), 3),
        })
    return clusters


def _compute_temporal_entropy(clusters):
    """Compute Shannon entropy of the temporal distribution."""
    total = sum(c["count"] for c in clusters)
    if total == 0: return 0
    entropy = 0
    for c in clusters:
        p = c["count"] / total
        if p > 0:
            entropy -= p * math.log2(p)
    return round(entropy, 4)


def map_temporal():
    """Generate the temporal resonance map."""
    modules = _scan_module_timestamps()
    clusters = _compute_temporal_clusters(modules)
    entropy = _compute_temporal_entropy(clusters)

    wave_counts = {}
    for m in modules:
        w = m["wave"]
        if w > 0:
            wave_counts[w] = wave_counts.get(w, 0) + 1

    peak_wave = max(wave_counts, key=wave_counts.get) if wave_counts else 0
    active_waves = len(wave_counts)
    total_modules = len(modules)

    # Temporal "heartbeat" — average time between module creations sorted by creation time
    sorted_times = sorted(m["created"] for m in modules if m["created"])
    if len(sorted_times) > 1:
        diffs = [sorted_times[i+1] - sorted_times[i] for i in range(len(sorted_times)-1)]
        avg_heartbeat = round(sum(diffs) / len(diffs), 2)
        heartbeat_freq = round(1 / max(1, avg_heartbeat), 6)
    else:
        avg_heartbeat = 0
        heartbeat_freq = 0

    result = {
        "action": "temporal_resonance_map",
        "total_modules": total_modules,
        "active_waves": active_waves,
        "peak_wave": peak_wave,
        "peak_wave_count": wave_counts.get(peak_wave, 0),
        "temporal_entropy": entropy,
        "avg_heartbeat_sec": avg_heartbeat,
        "heartbeat_freq": heartbeat_freq,
        "clusters": clusters,
        "wave_distribution": dict(sorted(wave_counts.items())),
        "timestamp": time.time(),
    }

    log = _load(MAP_LOG, {"maps": []})
    log["maps"].append(result)
    log["maps"] = log["maps"][-50:]
    _save(MAP_LOG, log)

    return result


def handler(payload=None, context=None):
    return map_temporal()


def coherence_vitals() -> dict:
    r = map_temporal()
    return {
        "temporal_entropy": r.get("temporal_entropy", 0),
        "heartbeat_freq": r.get("heartbeat_freq", 0),
        "active_waves": r.get("active_waves", 0),
    }


def resonates_with():
    return ["resonance_graph", "wave_log", "organism_genome", "signal_loom"]
