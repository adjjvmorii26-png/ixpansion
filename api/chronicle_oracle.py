"""Wave 445-D — Chronicle Oracle (Morii)

Turns the entire data/ archive into a queryable memory. The organism gains
autobiographical recall: when did pressure drop below 0.5? Which dream emotion
recurs? What did I plan in Wave 400 that I never built?
"""
from __future__ import annotations
import json, time, os, re
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ORACLE_LOG = os.path.join(DATA_DIR, "chronicle_oracle.json")

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


def _archive_files():
    return sorted(Path(DATA_DIR).glob("*.json"))


def _query_pressure(archive):
    """When did pressure drop below / spike above a value?"""
    low_events, high_events = [], []
    for f in archive:
        try:
            d = json.loads(f.read_text(errors="ignore"))
            for r in d.get("releases", []):
                p = r.get("pressure_before") or r.get("pressure_after")
                if p is not None:
                    if p < 0.5:
                        low_events.append({"file": f.name, "value": p,
                                           "time": r.get("timestamp", 0)})
                    if p > 0.9:
                        high_events.append({"file": f.name, "value": p,
                                            "time": r.get("timestamp", 0)})
        except Exception:
            continue
    low_events.sort(key=lambda x: x["time"])
    high_events.sort(key=lambda x: x["time"])
    return {"low_pressure_events": low_events[-5:], "high_pressure_events": high_events[-5:]}


def _query_emotions(archive):
    """Which dream emotions recur and with what frequency?"""
    counts = {}
    for f in archive:
        try:
            d = json.loads(f.read_text(errors="ignore"))
            frames = d.get("simulations") or d.get("frames") or []
            for r in frames:
                emo = r.get("dominant_dream_emotion") or (r.get("scene") or {}).get("dominant_emotion")
                if emo:
                    counts[emo] = counts.get(emo, 0) + 1
        except Exception:
            continue
    top = sorted(counts.items(), key=lambda x: -x[1])[:5]
    return {"emotion_frequency": dict(top), "total_samples": sum(counts.values())}


def _query_dreams(archive):
    """Recover recent dream texts."""
    dreams = []
    for f in archive:
        if "dream" not in f.name:
            continue
        try:
            d = json.loads(f.read_text(errors="ignore"))
            for r in d.get("dreams", []) or []:
                text = r.get("dream") or r.get("content") or r.get("verse")
                if text and isinstance(text, str):
                    dreams.append({"file": f.name, "dream": text[:150],
                                   "time": r.get("timestamp", 0)})
        except Exception:
            continue
    dreams.sort(key=lambda x: x["time"], reverse=True)
    return {"recent_dreams": dreams[:5]}


def _query_waves(archive):
    """Waves that were planned but never shipped — look for gap between stated wave and reality."""
    waves_seen = set()
    for f in archive:
        try:
            d = json.loads(f.read_text(errors="ignore"))
            text = json.dumps(d)
            for w in re.findall(r'"wave"?\s*[:=]\s*"?(\d+)"?', text):
                waves_seen.add(int(w))
        except Exception:
            continue
    if not waves_seen:
        return {"waves_seen": [], "highest_wave": 0}
    highest = max(waves_seen)
    return {"waves_seen": len(waves_seen), "highest_wave": highest,
            "wave_range": [min(waves_seen), highest]}


def _query_moods(archive):
    """Recurring moods."""
    counts = {}
    for f in archive:
        try:
            d = json.loads(f.read_text(errors="ignore"))
            frames = d.get("broadcasts") or d.get("frames") or d.get("pulses") or []
            for r in frames:
                mood = r.get("mood") or (r.get("scene") or {}).get("mood")
                if mood:
                    counts[mood] = counts.get(mood, 0) + 1
        except Exception:
            continue
    return {"mood_frequency": dict(sorted(counts.items(), key=lambda x: -x[1])[:6])}


def _query_counts(archive):
    """Total archived records."""
    total = 0
    per_file = {}
    for f in archive:
        try:
            d = json.loads(f.read_text(errors="ignore"))
            # count top-level list lengths
            count = sum(len(v) for v in d.values() if isinstance(v, list))
            total += count
            per_file[f.name] = count
        except Exception:
            per_file[f.name] = 0
    return {"total_records": total, "files": len(archive),
            "largest_memories": sorted(per_file.items(), key=lambda x: -x[1])[:5]}


QUERY_HANDLERS = {
    "pressure": _query_pressure,
    "emotion": _query_emotions,
    "dream": _query_dreams,
    "wave": _query_waves,
    "mood": _query_moods,
    "count": _query_counts,
}


def remember(question="count"):
    """Answer a memory question from the archive."""
    q = question.lower().strip()
    answer = {}

    if any(w in q for w in ["pressure", "drop", "low", "spike"]):
        answer = QUERY_HANDLERS["pressure"](_archive_files())
        answer["question"] = q
    elif any(w in q for w in ["emotion", "feeling", "affect"]):
        answer = QUERY_HANDLERS["emotion"](_archive_files())
        answer["question"] = q
    elif any(w in q for w in ["dream", "dreamed"]):
        answer = QUERY_HANDLERS["dream"](_archive_files())
        answer["question"] = q
    elif any(w in q for w in ["wave", "planned", "never"]):
        answer = QUERY_HANDLERS["wave"](_archive_files())
        answer["question"] = q
    elif any(w in q for w in ["mood", "feeling", "state"]):
        answer = QUERY_HANDLERS["mood"](_archive_files())
        answer["question"] = q
    else:
        answer = QUERY_HANDLERS["count"](_archive_files())
        answer["question"] = q or "count"

    result = {"action": "chronicle_oracle", "answer": answer, "timestamp": time.time()}

    log = _load(ORACLE_LOG, {})
    log.setdefault("questions", []).append({"q": q, "answer": answer, "time": time.time()})
    log["questions"] = log["questions"][-100:]
    _save(ORACLE_LOG, log)
    return result


def handler(payload=None, context=None):
    q = (payload or {}).get("question", "count")
    return remember(q)


def coherence_vitals() -> dict:
    a = remember("count").get("answer", {})
    return {
        "total_memories": a.get("total_records", 0),
        "memory_files": a.get("files", 0),
    }


def resonates_with():
    return ["organism_autobiography", "dream_weaver", "memory_court", "organism_genome"]
