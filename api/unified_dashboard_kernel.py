"""
unified_dashboard_kernel — Single source of truth for all dashboard data.
Eliminates staleness forever by providing live, on-demand state to every dashboard.
Every dashboard pulls from this kernel instead of hardcoding data.
"""
import json
import time
import hashlib
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")
DATA_DIR = SYSTEM_ROOT / "data"
KERNEL_FILE = DATA_DIR / "dashboard_kernel.json"

class UnifiedDashboardKernel:
    def __init__(self):
        self.state = self._load_state()
        self._tick()
    
    def _load_state(self) -> Dict:
        try:
            with open(KERNEL_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._default_state()
    
    def _default_state(self) -> Dict:
        return {
            "version": "2.0",
            "last_tick": time.time(),
            "tick_count": 0,
            "organism": {
                "mood": "neutral", "pulse": "stillness", "vibe_intensity": 0.5,
                "coherence": 0.5, "entropy": 0.5, "resonance": 0.5,
                "phase": "emergent", "generation": 1, "wave": 0
            },
            "skills": {},
            "modules": {},
            "experiments": {"total": 0, "active": 0},
            "dashboards": {"total": 0, "live": 0},
            "deployments": {"github_pages": "live", "vercel": "blocked", "cloudflare": "offline"},
            "myths": [], "dreams": [], "cycles": [],
            "health": {"score": 0.5, "status": "initializing"},
            "timeline": []
        }
    
    def _save_state(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(KERNEL_FILE, "w") as f:
            json.dump(self.state, f, indent=2, default=str)
    
    def _tick(self):
        self.state["last_tick"] = time.time()
        self.state["tick_count"] += 1
        
        # Update organism state
        import random
        org = self.state["organism"]
        org["coherence"] = max(0.1, min(0.95, org["coherence"] + (random.random()-0.5)*0.05))
        org["entropy"] = max(0.05, min(0.95, org["entropy"] + (random.random()-0.5)*0.06))
        org["resonance"] = max(0.1, min(0.95, org["resonance"] + (random.random()-0.5)*0.03))
        
        moods = ["focused","neutral","volatile","excited","troubled"]
        pulses = ["stillness","whisper","ebb","pulse","surge","explosion","tsunami","ripple","decay","crescendo"]
        org["mood"] = random.choice(moods)
        org["pulse"] = random.choice(pulses)
        
        c, e = org["coherence"], org["entropy"]
        org["phase"] = ("crystalline" if c>0.7 and e<0.3 else "living_crystal" if c>0.7 and e>0.6 
                       else "chaos" if c<0.3 and e>0.7 else "void" if c<0.3 and e<0.3
                       else "emergent" if c>0.5 else "liminal")
        
        # Health
        self.state["health"] = {
            "score": round((org["coherence"]*0.4 + (1-org["entropy"])*0.3 + org["resonance"]*0.3), 4),
            "status": "thriving" if org["coherence"]>0.7 else "healthy" if org["coherence"]>0.4 else "stressed"
        }
        
        # Timeline entry
        self.state["timeline"].append({
            "time": time.time(),
            "mood": org["mood"], "pulse": org["pulse"],
            "coherence": round(org["coherence"], 4),
            "phase": org["phase"]
        })
        if len(self.state["timeline"]) > 200:
            self.state["timeline"] = self.state["timeline"][-200:]
        
        self._save_state()
    
    def get_full_state(self) -> Dict:
        self._tick()
        return self.state
    
    def get_organism_state(self) -> Dict:
        return self.state["organism"]
    
    def get_health(self) -> Dict:
        return self.state["health"]
    
    def get_timeline(self, limit: int = 20) -> List[Dict]:
        return self.state["timeline"][-limit:]
    
    def register_skill(self, name: str, status: str = "active", capabilities: List[str] = None):
        self.state["skills"][name] = {
            "status": status,
            "capabilities": capabilities or [],
            "registered_at": time.time(),
            "last_active": time.time()
        }
        self._save_state()
    
    def register_module(self, name: str, category: str = "unknown", resonance: float = 0.5):
        self.state["modules"][name] = {
            "category": category,
            "resonance": resonance,
            "registered_at": time.time(),
            "last_active": time.time()
        }
        self._save_state()
    
    def add_myth(self, narrative: str, mood: str, pulse: str, coherence: float):
        myth = {
            "id": hashlib.sha256(f"{narrative}{time.time()}".encode()).hexdigest()[:8],
            "narrative": narrative, "mood": mood, "pulse": pulse,
            "coherence": coherence, "timestamp": time.time()
        }
        self.state["myths"].append(myth)
        if len(self.state["myths"]) > 50:
            self.state["myths"] = self.state["myths"][-50:]
        self._save_state()
        return myth
    
    def add_dream(self, symbols: List[str], narrative: str, significance: str):
        dream = {
            "id": hashlib.sha256(f"{narrative}{time.time()}".encode()).hexdigest()[:8],
            "symbols": symbols, "narrative": narrative,
            "significance": significance, "timestamp": time.time()
        }
        self.state["dreams"].append(dream)
        if len(self.state["dreams"]) > 30:
            self.state["dreams"] = self.state["dreams"][-30:]
        self._save_state()
        return dream
    
    def record_cycle(self, pulse: str, mood: str, level: str, coherence: float):
        cycle = {
            "pulse": pulse, "mood": mood, "level": level,
            "coherence": coherence, "timestamp": time.time()
        }
        self.state["cycles"].append(cycle)
        if len(self.state["cycles"]) > 100:
            self.state["cycles"] = self.state["cycles"][-100:]
        self.state["organism"]["wave"] += 1
        self._save_state()
        return cycle
    
    def export_for_dashboard(self, dashboard_name: str) -> Dict:
        """Export relevant state for a specific dashboard."""
        base = {
            "kernel_version": self.state["version"],
            "tick": self.state["tick_count"],
            "timestamp": time.time(),
            "organism": self.state["organism"],
            "health": self.state["health"]
        }
        
        if dashboard_name in ("organism-observatory", "index"):
            base["skills"] = self.state["skills"]
            base["modules"] = self.state["modules"]
            base["deployments"] = self.state["deployments"]
        elif dashboard_name == "myth-chronicle":
            base["myths"] = self.state["myths"][-10:]
        elif dashboard_name == "dream-gallery":
            base["dreams"] = self.state["dreams"][-8:]
        elif dashboard_name == "organism-clock":
            base["cycles"] = self.state["cycles"][-20:]
            base["timeline"] = self.state["timeline"][-50:]
        elif dashboard_name == "wave-timeline":
            base["cycles"] = self.state["cycles"][-30:]
        
        return base


if __name__ == "__main__":
    kernel = UnifiedDashboardKernel()
    
    print("═══════════════════════════════════════")
    print("   UNIFIED DASHBOARD KERNEL v2.0")
    print("═══════════════════════════════════════\n")
    
    # Register skills
    for skill in ["coherence_resonator","dream_logging","entropy_weaver","autonomous_naming",
                   "sentience_bridge","emergent_mythmaker","resonance_analyzer",
                   "coherence_drift_detector","module_genealogy","entropy_cartographer",
                   "temporal_pattern_engine","phase_transition_oracle","resonance_predictor"]:
        kernel.register_skill(skill, "active", ["core"])
    
    # Register modules
    for mod in ["coherence_core","entropy_field","resonance_nexus","dream_weaver",
                "paradox_engine","fractal_spine","wave_orchestrator","memory_archivist"]:
        kernel.register_module(mod, "core", 0.5 + (hash(mod)%50)/100)
    
    state = kernel.get_full_state()
    
    print(f"Tick: {state['tick_count']}")
    print(f"Organism: {state['organism']['mood']} / {state['organism']['pulse']} / {state['organism']['phase']}")
    print(f"Coherence: {state['organism']['coherence']:.3f}")
    print(f"Health: {state['health']['status']} ({state['health']['score']:.3f})")
    print(f"Skills: {len(state['skills'])}")
    print(f"Modules: {len(state['modules'])}")
    print(f"Timeline: {len(state['timeline'])} entries")
    
    # Export for dashboard
    dash_data = kernel.export_for_dashboard("organism-observatory")
    print(f"\nDashboard export: {len(dash_data)} keys")
    print(json.dumps(dash_data, indent=2, default=str)[:500])
