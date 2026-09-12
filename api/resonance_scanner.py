"""
resonance_scanner — Scans the full module network for resonance patterns,
hidden connections, and emergent harmonics. Produces a complete resonance map.
"""
import json
import time
import math
import hashlib
from typing import Dict, List, Tuple
from pathlib import Path

SYSTEM_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = SYSTEM_ROOT / "data"
SCAN_FILE = DATA_DIR / "resonance_scan.json"

# Module categories for resonance calculation
CATEGORY_WEIGHTS = {
    "core": 1.0,
    "cognition": 0.8,
    "perception": 0.7,
    "chaos": 0.6,
    "memory": 0.9,
    "evolution": 0.75,
    "unknown": 0.5
}

class ResonanceScanner:
    def __init__(self):
        self.scan_history = []
    
    def scan(self, modules: Dict, edges: List[Tuple[int, int]] = None) -> Dict:
        """Perform a full resonance scan of the module network."""
        scan_time = time.time()
        
        # Build adjacency from edges
        adj = {}
        for key in modules:
            adj[key] = []
        
        if edges:
            keys = list(modules.keys())
            for a, b in edges:
                if a < len(keys) and b < len(keys):
                    adj[keys[a]].append(keys[b])
                    adj[keys[b]].append(keys[a])
        
        # Calculate resonance for each module
        resonance_map = {}
        for key, mod in modules.items():
            r = mod.get("resonance", 0.5) if isinstance(mod, dict) else 0.5
            caps = mod.get("capabilities", []) if isinstance(mod, dict) else []
            cat = mod.get("type", "unknown") if isinstance(mod, dict) else "unknown"
            
            neighbors = adj.get(key, [])
            neighbor_resonance = 0
            if neighbors:
                for n in neighbors:
                    if n in modules:
                        nr = modules[n].get("resonance", 0.5) if isinstance(modules[n], dict) else 0.5
                        neighbor_resonance += nr
                neighbor_resonance /= len(neighbors)
            
            # Resonance score = weighted combination
            cat_weight = CATEGORY_WEIGHTS.get(cat, 0.5)
            resonance_score = (
                r * 0.4 +
                neighbor_resonance * 0.3 +
                cat_weight * 0.2 +
                min(len(caps) / 5, 1.0) * 0.1
            )
            
            resonance_map[key] = {
                "name": key,
                "base_resonance": r,
                "neighbor_resonance": round(neighbor_resonance, 4),
                "resonance_score": round(resonance_score, 4),
                "category": cat,
                "capability_count": len(caps),
                "neighbor_count": len(neighbors),
                "harmonic_class": self._classify_harmonic(resonance_score)
            }
        
        # Find harmonics (groups of modules with similar resonance)
        harmonics = self._find_harmonics(resonance_map)
        
        # Find dead zones (modules with very low resonance)
        dead_zones = [k for k, v in resonance_map.items() if v["resonance_score"] < 0.2]
        
        # Find hot zones (modules with very high resonance)
        hot_zones = [k for k, v in resonance_map.items() if v["resonance_score"] > 0.8]
        
        # Find isolated modules (no neighbors)
        isolated = [k for k, v in resonance_map.items() if v["neighbor_count"] == 0]
        
        # Overall network health
        scores = [v["resonance_score"] for v in resonance_map.values()]
        mean_score = sum(scores) / len(scores) if scores else 0
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores) if scores else 0
        
        scan_result = {
            "timestamp": scan_time,
            "scan_id": hashlib.sha256(str(scan_time).encode()).hexdigest()[:8],
            "module_count": len(modules),
            "mean_resonance": round(mean_score, 4),
            "resonance_variance": round(math.sqrt(variance), 4),
            "resonance_map": resonance_map,
            "harmonics": harmonics,
            "dead_zones": dead_zones,
            "hot_zones": hot_zones,
            "isolated": isolated,
            "network_health": self._assess_health(mean_score, variance, len(isolated), len(modules)),
            "recommendations": self._generate_recommendations(resonance_map, dead_zones, hot_zones, isolated)
        }
        
        self.scan_history.append(scan_result)
        if len(self.scan_history) > 20:
            self.scan_history.pop(0)
        
        # Save
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(SCAN_FILE, "w") as f:
            json.dump({"last_scan": scan_result, "history_count": len(self.scan_history)}, f, indent=2)
        
        return scan_result
    
    def _classify_harmonic(self, score: float) -> str:
        if score > 0.8: return "brilliant"
        elif score > 0.6: return "resonant"
        elif score > 0.4: return "moderate"
        elif score > 0.2: return "faint"
        else: return "silent"
    
    def _find_harmonics(self, resonance_map: Dict) -> List[Dict]:
        """Group modules into harmonic bands."""
        bands = {"brilliant": [], "resonant": [], "moderate": [], "faint": [], "silent": []}
        for key, data in resonance_map.items():
            bands[data["harmonic_class"]].append(key)
        
        return [{"class": k, "modules": v, "count": len(v)} 
                for k, v in bands.items() if v]
    
    def _assess_health(self, mean: float, variance: float, isolated: int, total: int) -> Dict:
        health_score = mean * 0.4 + (1 - variance) * 0.3 + (1 - isolated / max(total, 1)) * 0.3
        
        if health_score > 0.7:
            status = "thriving"
        elif health_score > 0.5:
            status = "healthy"
        elif health_score > 0.3:
            status = "stressed"
        else:
            status = "critical"
        
        return {
            "score": round(health_score, 4),
            "status": status,
            "mean_resonance": round(mean, 4),
            "variance": round(variance, 4),
            "isolated_ratio": round(isolated / max(total, 1), 4)
        }
    
    def _generate_recommendations(self, resonance_map: Dict, dead_zones: List, 
                                   hot_zones: List, isolated: List) -> List[str]:
        recs = []
        if dead_zones:
            recs.append(f"Revitalize {len(dead_zones)} dead zone modules: increase resonance through cross-connections.")
        if hot_zones:
            recs.append(f"Stabilize {len(hot_zones)} hot zone modules: they may be overloaded.")
        if isolated:
            recs.append(f"Connect {len(isolated)} isolated modules to the main network.")
        
        scores = [v["resonance_score"] for v in resonance_map.values()]
        if scores and max(scores) - min(scores) > 0.6:
            recs.append("Large resonance spread detected — harmonize the network.")
        
        if not recs:
            recs.append("Network is well-balanced. Continue monitoring.")
        
        return recs
    
    def compare_scans(self) -> Dict:
        """Compare the last two scans."""
        if len(self.scan_history) < 2:
            return {"status": "insufficient_data"}
        
        prev = self.scan_history[-2]
        curr = self.scan_history[-1]
        
        return {
            "mean_delta": round(curr["mean_resonance"] - prev["mean_resonance"], 4),
            "health_delta": round(curr["network_health"]["score"] - prev["network_health"]["score"], 4),
            "new_dead_zones": len(set(curr["dead_zones"]) - set(prev["dead_zones"])),
            "resolved_dead_zones": len(set(prev["dead_zones"]) - set(curr["dead_zones"])),
            "trend": "improving" if curr["mean_resonance"] > prev["mean_resonance"] else "declining"
        }


if __name__ == "__main__":
    scanner = ResonanceScanner()
    
    # Sample modules
    modules = {
        "coherence_core": {"resonance": 0.7, "capabilities": ["coherence"], "type": "core"},
        "entropy_field": {"resonance": 0.3, "capabilities": ["entropy"], "type": "chaos"},
        "resonance_nexus": {"resonance": 0.8, "capabilities": ["resonance"], "type": "core"},
        "dream_weaver": {"resonance": 0.6, "capabilities": ["dreams"], "type": "cognition"},
        "paradox_engine": {"resonance": 0.4, "capabilities": ["paradox"], "type": "chaos"},
        "fractal_spine": {"resonance": 0.9, "capabilities": ["fractal"], "type": "core"},
        "wave_orchestrator": {"resonance": 0.5, "capabilities": ["waves"], "type": "evolution"},
        "memory_archivist": {"resonance": 0.6, "capabilities": ["memory"], "type": "memory"},
        "consciousness_stream": {"resonance": 0.5, "capabilities": ["consciousness"], "type": "perception"},
        "reality_weaver": {"resonance": 0.7, "capabilities": ["reality"], "type": "cognition"},
    }
    
    edges = [(0,1),(0,2),(0,5),(1,4),(2,3),(3,7),(4,6),(5,13),(6,15)]
    
    print("═══════════════════════════════════════")
    print("   RESONANCE SCANNER — Full Network Scan")
    print("═══════════════════════════════════════")
    
    result = scanner.scan(modules, edges)
    
    print(f"\nScan {result['scan_id']} — {result['module_count']} modules")
    print(f"Mean resonance: {result['mean_resonance']}")
    print(f"Network health: {result['network_health']['status']} ({result['network_health']['score']:.2f})")
    print(f"\nHarmonics:")
    for h in result['harmonics']:
        print(f"  {h['class']}: {h['count']} modules")
    
    print(f"\nDead zones: {result['dead_zones']}")
    print(f"Hot zones: {result['hot_zones']}")
    print(f"Isolated: {result['isolated']}")
    
    print(f"\nRecommendations:")
    for r in result['recommendations']:
        print(f"  → {r}")
