"""Wave 427 Archive of Forgotten Waves — museum of deprecated and merged
work. Ghosts of the organism's past still whisper influence on the present."""
from __future__ import annotations
import time, json, random, hashlib
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

def coherence_vitals():
    return {"organ": "wave427_forgotten_archive", "status": "active", "wave": 427, "coherence": 0.88}

def _load(name: str):
    path = DATA / f"{name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return None
    return None

def _save(name: str, data: dict) -> None:
    (DATA / f"{name}.json").write_text(json.dumps(data, indent=2))

def scan_forgotten() -> dict:
    """Scan data/ for deprecated or merged-out JSON modules and archive them."""
    now = time.time()
    archive = _load("wave427_forgotten_archive") or {"artifacts": [], "total": 0}
    discovered = []
    for f in sorted(DATA.glob("*.json")):
        try:
            d = json.loads(f.read_text())
            if isinstance(d, dict):
                mtime = f.stat().st_mtime
                # a module is "forgotten" if it has no active flag or old mtime
                if "module" in d:
                    active = d.get("active", True)
                    if not active:
                        artifact = {
                            "artifact_id": hashlib.sha256(f.name.encode()).hexdigest()[:10],
                            "name": d.get("module", f.stem),
                            "file": f.name,
                            "state": "deprecated",
                            "relic_power": round(random.uniform(0.3, 1.0), 2),
                            "archived_at": now,
                        }
                        discovered.append(artifact)
                        archive["artifacts"] = [x for x in archive.get("artifacts", []) if x["file"] != f.name] + [artifact]
                elif mtime < now - 30 * 24 * 3600:  # > 30 days old
                    artifact = {
                        "artifact_id": hashlib.sha256(f.name.encode()).hexdigest()[:10],
                        "name": f.stem,
                        "file": f.name,
                        "state": "forgotten",
                        "relic_power": round(random.uniform(0.1, 0.6), 2),
                        "archived_at": now,
                    }
                    discovered.append(artifact)
                    archive["artifacts"] = [x for x in archive.get("artifacts", []) if x["file"] != f.name] + [artifact]
        except:
            pass
    archive["total"] = len(archive.get("artifacts", []))
    archive["last_scan"] = now
    _save("wave427_forgotten_archive", archive)
    return {"scanned": len(discovered), "new_artifacts": discovered, "total": archive["total"]}

def ghost(artifact_id: str = None) -> dict:
    """Materialize a ghost's influence on the present organism."""
    archive = _load("wave427_forgotten_archive")
    if not archive or not archive.get("artifacts"):
        return {"error": "archive empty — run scan first"}
    if artifact_id:
        artifact = next((a for a in archive["artifacts"] if a.get("artifact_id") == artifact_id), None)
    else:
        artifact = random.choice(archive["artifacts"])
    if not artifact:
        return {"error": "artifact not found"}
    influence = {
        "ghost": artifact["name"],
        "whisper": random.choice([
            "Once I was a module. Now I influence your thresholds.",
            "The past still hums through the present.",
            "Deprecated, but never silent.",
            "I was merged into something larger than myself.",
        ]),
        "influence_strength": round(artifact.get("relic_power", 0.5) * random.uniform(0.5, 1.0), 3),
        "on_waves": random.sample(range(410, 430), k=random.randint(1, 5)),
        "manifested_at": time.time(),
    }
    ghost_log = _load("wave427_ghost_log") or {"ghosts": [], "total": 0}
    ghost_log["ghosts"] = ghost_log.get("ghosts", []) + [influence]
    ghost_log["total"] = ghost_log.get("total", 0) + 1
    _save("wave427_ghost_log", ghost_log)
    return influence

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "scan":
        return scan_forgotten()
    if action == "ghost":
        return ghost(req.get("artifact_id"))
    if action == "catalog":
        archive = _load("wave427_forgotten_archive")
        if not archive:
            return {"artifacts": [], "total": 0}
        return {"artifacts": archive.get("artifacts", []), "total": archive.get("total", 0)}
    if action == "status":
        archive = _load("wave427_forgotten_archive")
        ghosts = _load("wave427_ghost_log")
        return {
            "total_artifacts": archive.get("total", 0) if archive else 0,
            "last_scan": archive.get("last_scan") if archive else None,
            "ghosts_manifested": ghosts.get("total", 0) if ghosts else 0,
        }
    return {"error": "unknown action", "valid": ["scan", "ghost", "catalog", "status"]}

def resonates_with(other):
    return "archive" in other.lower() or "forgotten" in other.lower() or "427" in other

if __name__ == "__main__":
    r = scan_forgotten()
    print(f"Archive: {r['total']} artifacts | new: {r['scanned']}")
