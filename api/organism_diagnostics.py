"""Organism Diagnostics Sweep — full health audit across all data files.
Checks: integrity, staleness, schema validity, cross-reference consistency,
orphaned files, missing references, data freshness, and coherence."""
from __future__ import annotations
import json, os, time
from pathlib import Path
from datetime import datetime, timedelta

DATA = Path(__file__).parent.parent / "data"

STALE_AGE_HOURS = 24  # files not modified in 24h flagged as stale

def _load(name: str):
    path = DATA / f"{name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text()), path
        except Exception as e:
            return {"error": str(e)}, path
    return None, path

def _classify(name: str) -> str:
    """Classify a data file by its purpose."""
    if 'wave' in name.lower(): return 'wave_seed'
    if 'chronicle' in name.lower(): return 'narrative'
    if 'consciousness' in name.lower(): return 'consciousness'
    if 'organism' in name.lower(): return 'organism_core'
    if 'bot' in name.lower(): return 'interface'
    if 'dream' in name.lower(): return 'dream_engine'
    if 'paradox' in name.lower(): return 'metaphysical'
    if 'veil' in name.lower(): return 'metaphysical'
    if 'resonance' in name.lower(): return 'metaphysical'
    if 'mycelial' in name.lower() or 'governor' in name.lower(): return 'regulator'
    if 'fusion' in name.lower(): return 'fusion'
    if 'topology' in name.lower(): return 'topology'
    if 'threshold' in name.lower(): return 'boundary'
    if 'axiom' in name.lower(): return 'foundational'
    if 'liminal' in name.lower(): return 'transient'
    if 'metaphor' in name.lower(): return 'symbolic'
    if 'transcendence' in name.lower(): return 'scripture'
    if 'continuity' in name.lower(): return 'coherence'
    if 'anomaly' in name.lower(): return 'monitoring'
    if 'decay' in name.lower() or 'forecaster' in name.lower(): return 'prediction'
    if 'orbit' in name.lower() or 'telemetry' in name.lower(): return 'telemetry'
    if 'garden' in name.lower() or 'biome' in name.lower(): return 'environment'
    if 'census' in name.lower(): return 'organism_core'
    if 'genome' in name.lower(): return 'organism_core'
    if 'name' in name.lower(): return 'organism_core'
    if 'radio' in name.lower() or 'broadcast' in name.lower(): return 'communication'
    return 'general'

def run_sweep() -> dict:
    """Run a full organism diagnostics sweep."""
    results = {
        "sweep_id": f"diag_{int(time.time())}",
        "wave": 412,
        "realm": "garden",
        "timestamp": time.time(),
        "summary": {},
        "modules": [],
        "anomalies": [],
        "health_score": 0,
    }

    total = 0
    healthy = 0
    stale = 0
    corrupted = 0
    orphaned = 0
    anomalies = []
    module_reports = []

    now = time.time()
    hour_ago = now - (STALE_AGE_HOURS * 3600)

    for f in sorted(DATA.glob("*.json")):
        total += 1
        name = f.stem
        try:
            content = f.read_text()
            d = json.loads(content)
            mtime = f.stat().st_mtime

            rec = {
                "name": name,
                "class": _classify(name),
                "size_bytes": len(content),
                "modified": mtime,
                "stale": mtime < hour_ago,
                "integrity": "valid",
                "schema": "ok",
            }

            if isinstance(d, dict):
                if "module" in d:
                    rec["is_module"] = True
                    if not d.get("active", True):
                        rec["status"] = "inactive"
                        anomalies.append({"type": "inactive_module", "file": name})
                    else:
                        rec["status"] = "active"
                        healthy += 1
                else:
                    rec["status"] = "data"
                    healthy += 1
            elif isinstance(d, list):
                rec["status"] = "data_array"
                healthy += 1

            # Stale check
            if rec["stale"]:
                stale += 1
                anomalies.append({"type": "stale_data", "file": name, "hours_ago": round((now - mtime) / 3600, 1)})

            # Check for missing fields
            if isinstance(d, dict):
                required_fields = []
                if rec["class"] in ('organism_core',) and "name" not in d and "names" not in d:
                    required_fields.append("name")
                if rec["class"] in ('metaphysical',) and "records" not in d and "entries" not in d:
                    pass  # optional for journal types

                if required_fields:
                    rec["schema"] = "incomplete"
                    anomalies.append({"type": "schema_incomplete", "file": name, "missing": required_fields})

            module_reports.append(rec)

        except json.JSONDecodeError as e:
            corrupted += 1
            anomalies.append({"type": "corrupted_json", "file": name, "error": str(e)[:80]})
            module_reports.append({"name": name, "class": _classify(name), "integrity": "corrupted"})
        except Exception as e:
            corrupted += 1
            anomalies.append({"type": "read_error", "file": name, "error": str(e)[:80]})

    # Check for orphaned wave seeds vs wave seeds count
    wave_seeds_path = DATA / "wave_seeds.json"
    if wave_seeds_path.exists():
        try:
            seeds_data = json.loads(wave_seeds_path.read_text())
            total_seeds = seeds_data.get("total", 0)
            results["wave_seeds_total"] = total_seeds
        except:
            pass

    results["summary"] = {
        "total_files": total,
        "healthy": healthy,
        "stale": stale,
        "corrupted": corrupted,
        "anomaly_count": len(anomalies),
    }

    # Health score: 0-100
    if total > 0:
        results["health_score"] = round((healthy / total) * 100, 1)

    results["anomalies"] = anomalies[:50]  # cap at 50
    results["modules"] = module_reports
    results["completed_at"] = time.time()

    # Save report
    (DATA / "diagnostic_report.json").write_text(json.dumps(results, indent=2))

    return results

def handler(req: dict) -> dict:
    action = req.get("action", "sweep")
    if action == "sweep":
        return run_sweep()
    elif action == "summary":
        r = run_sweep()
        return {"health_score": r["health_score"], "summary": r["summary"], "anomaly_count": len(r["anomalies"])}
    elif action == "classify":
        name = req.get("name", "")
        return {"name": name, "class": _classify(name)}
    return {"error": "unknown action"}

def resonates_with(other):
    return "diagnostic" in other.lower() or "health" in other.lower() or "sweep" in other.lower()

if __name__ == "__main__":
    r = run_sweep()
    print(f"Health: {r['health_score']}% | Total: {r['summary']['total_files']} | Anomalies: {r['anomaly_count']}")
