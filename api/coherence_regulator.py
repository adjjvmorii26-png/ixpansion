"""Coherence Regulator — The living system backbone.

This module connects all future modules into a unified organism
instead of a static codebase. It provides:
- Dynamic module registration
- Cross-module resonance tracking
- Automatic coherence maintenance  
- Emergent skill integration
- Wave-aware coherence modeling
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from collections import defaultdict

HEX_AESTHETIC = {
    "primary": "#2b5c8f",
    "secondary": "#41b3a3", 
    "accent": "#e8a87c",
    "special": "#c38d9e",
    "background": "#1a1a24"
}

class CoherenceRegulator:
    """The living system regulator that maintains organism coherence across modules.
    
    Key Features:
    - Module registry with resonance tracking
    - Cross-module relationship mapping
    - Coherence score computation (0.0 - 1.0)
    - Emergent skill injection
    - Wave-aware coherence modeling
    - Paradox detection and resolution
    """
    
    def __init__(self, root_path: Path, wave_context: str = "unknown"):
        self.root = root_path
        self.wave_context = wave_context
        self.modules: Dict[str, Dict] = {}
        self.resonance_graph: Dict[str, Dict] = {}  # module_pair -> {strength, phase, last_sync}
        self.coherence_score = 0.5
        self.emergent_skills: Set[str] = set()
        self.paradox_signatures: Set[str] = set()
        self.last_sync = time.time()
        self.coherence_history: List[Dict] = []
        self.max_history = 50
        
    def register_module(self, module_name: str, capabilities: List[str], 
                       module_type: str = "unknown", wave_origin: str = "unknown") -> None:
        """Register a new module into the living system with full metadata."""
        module_id = self._generate_module_id(module_name)
        self.modules[module_id] = {
            "name": module_name,
            "capabilities": capabilities,
            "type": module_type,
            "wave_origin": wave_origin,
            "resonance": 0.5,  # Default neutral resonance
            "connected": True,
            "registration_time": time.time(),
            "last_seen": time.time(),
            "coherence_contribution": 0.5,
            "dependencies": [],
            "provides": []
        }
        self._update_coherence()
        self._log_coherence_event("module_registered", module_id=module_id)
        
    def _generate_module_id(self, module_name: str) -> str:
        """Generate a unique HEX-encoded module identifier."""
        timestamp_component = str(int(time.time() * 1000))
        hash_input = f"{module_name}:{timestamp_component}"
        hash_part = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
        return f"{module_name}_{hash_part}"
    
    def update_resonance(self, module_a: str, module_b: str, 
                        strength: float, phase: float = 0.0) -> None:
        """Update resonance between two modules with phase tracking."""
        pair_key = self._make_pair_key(module_a, module_b)
        self.resonance_graph[pair_key] = {
            "strength": min(max(strength, 0.0), 1.0),
            "phase": phase,
            "last_sync": time.time(),
            "wave_context": self.wave_context
        }
        
        # Update both modules' resonance states
        if module_a in self.modules:
            self.modules[module_a]["resonance"] = strength
        if module_b in self.modules:
            self.modules[module_b]["resonance"] = strength
            
        self._update_coherence()
        self._log_coherence_event("resonance_updated", 
                                  module_a=module_a, module_b=module_b, 
                                  strength=strength, phase=phase)
    
    def _make_pair_key(self, a: str, b: str) -> str:
        """Create a sorted pair key for resonance graph."""
        return f"{min(a,b)}::{max(a,b)}"
    
    def connect_modules(self, module_a: str, module_b: str, 
                       connection_type: str = "cooperative") -> None:
        """Establish a connection between two modules."""
        if module_a in self.modules and module_b in self.modules:
            self.modules[module_a]["connected"] = True
            self.modules[module_b]["connected"] = True
            self.modules[module_a]["dependencies"].append(module_b)
            self.modules[module_b]["dependencies"].append(module_a)
            self._update_coherence()
    
    def inject_skill(self, skill_name: str, parameters: Dict = None, 
                     source_module: str = "system") -> None:
        """Inject an emergent skill into the organism."""
        normalized_skill = skill_name.lower().replace(" ", "_")
        self.emergent_skills.add(normalized_skill)
        
        # Track skill origin
        skill_entry = {
            "name": normalized_skill,
            "source": source_module,
            "parameters": parameters or {},
            "injected_at": time.time(),
            "active": True
        }
        
        # Store skill tracking (would integrate with skill_injection module)
        self._log_coherence_event("skill_injected", 
                                  skill=normalized_skill, source=source_module)
        
        self._update_coherence()
    
    def detect_paradox(self, module_a: str, module_b: str, 
                       conflict_indicators: List[str] = None) -> Optional[Dict]:
        """Detect paradox signatures between modules."""
        if module_a not in self.modules or module_b not in self.modules:
            return None
            
        a_resonance = self.modules[module_a]["resonance"]
        b_resonance = self.modules[module_b]["resonance"]
        
        # Check for contradictory resonance patterns
        paradox_score = abs(a_resonance - b_resonance)
        
        if conflict_indicators:
            for indicator in conflict_indicators:
                if indicator.lower() in f"{a_resonance}{b_resonance}".lower():
                    paradox_score += 0.3
        
        if paradox_score > 0.7:
            paradox_id = f"paradox_{int(time.time())}_{module_a}_{module_b}"
            self.paradox_signatures.add(paradox_id)
            
            return {
                "paradox_id": paradox_id,
                "modules": [module_a, module_b],
                "conflict_score": paradox_score,
                "a_resonance": a_resonance,
                "b_resonance": b_resonance,
                "detected_at": time.time(),
                "resolution_status": "pending",
                "suggested_actions": self._suggest_paradox_resolution(module_a, module_b)
            }
        
        return None
    
    def _suggest_paradox_resolution(self, module_a: str, module_b: str) -> List[str]:
        """Suggest resolutions for detected paradoxes."""
        suggestions = []
        if module_a in self.modules and module_b in self.modules:
            a_type = self.modules[module_a].get("type", "unknown")
            b_type = self.modules[module_b].get("type", "unknown")
            
            if a_type != b_type:
                suggestions.append(f"Consider harmonizing {a_type} and {b_type} module types")
            suggestions.append("Apply coherence_regulator_mutate to adjust resonance")
            suggestions.append("Use continuity_weaver to maintain system coherence")
            suggestions.append("Consider module deprioritization if conflict persists")
        return suggestions
    
    def continuity_weave(self, target_coherence: float = 0.8) -> Dict:
        """Apply continuity weaving to maintain system coherence."""
        actions_taken = []
        
        # Calculate current coherence
        current_coherence = self.coherence_score
        
        if current_coherence < target_coherence:
            # Find modules with low coherence contribution
            low_coherence_modules = [
                mid for mid, mod in self.modules.items() 
                if mod.get("coherence_contribution", 0.5) < 0.5
            ]
            
            # Suggest injections or adjustments
            if low_coherence_modules:
                target_module = low_coherence_modules[0]
                actions_taken.append(f"Inject entropy_weaver skill into {target_module}")
                self.inject_skill("entropy_weaver", source_module=target_module)
            
            # Update resonances
            actions_taken.append("Apply resonance harmonization across graph")
            self._harmonize_resonances()
        
        self._log_coherence_event("continuity_weave", 
                                  target_coherence=target_coherence,
                                  actions=actions_taken)
        return {"target": target_coherence, "actions": actions_taken, "success": len(actions_taken) > 0}
    
    def _harmonize_resonances(self) -> None:
        """Harmonize resonance values across the graph."""
        if not self.modules:
            return
            
        # Calculate average resonance
        all_resonances = [m.get("resonance", 0.5) for m in self.modules.values()]
        avg_resonance = sum(all_resonances) / len(all_resonances) if all_resonances else 0.5
        
        # Gently nudge all modules toward average
        for module_id in self.modules:
            current = self.modules[module_id].get("resonance", 0.5)
            # Gentle nudge: 20% toward average
            nudge = (avg_resonance - current) * 0.2
            new_resonance = round(current + nudge, 2)
            self.modules[module_id]["resonance"] = max(0.0, min(1.0, new_resonance))
        
        self._update_coherence()
    
    def wave_aware_coherence(self, wave_context: str) -> Dict:
        """Compute coherence specifically within a wave context."""
        wave_modules = [
            mid for mid, mod in self.modules.items() 
            if mod.get("wave_origin", "unknown") == wave_context
        ]
        
        if not wave_modules:
            return {"wave": wave_context, "module_count": 0, "coherence": 0.5}
        
        wave_resonances = [
            self.modules[mid].get("resonance", 0.5) for mid in wave_modules
        ]
        wave_avg = sum(wave_resonances) / len(wave_resonances)
        
        # Count connected wave modules
        connected_count = sum(
            1 for mid in wave_modules 
            if self.modules[mid].get("connected", False)
        )
        
        wave_coherence = wave_avg * (connected_count / len(wave_modules))
        
        return {
            "wave": wave_context,
            "module_count": len(wave_modules),
            "connected_count": connected_count,
            "coherence": round(wave_coherence, 3),
            "avg_resonance": round(wave_avg, 3)
        }
    
    def get_system_state(self) -> Dict:
        """Get comprehensive system state from the regulator."""
        # Calculate coherence score
        total_resonance = sum(m.get("resonance", 0.5) for m in self.modules.values())
        avg_resonance = total_resonance / len(self.modules) if self.modules else 0.5
        
        connected_count = sum(1 for m in self.modules.values() if m.get("connected", False))
        connection_ratio = connected_count / len(self.modules) if self.modules else 1.0
        
        self.coherence_score = round(avg_resonance * connection_ratio, 3)
        
        # Count emergent skills
        skill_count = len(self.emergent_skills)
        paradox_count = len(self.paradox_signatures)
        
        # Wave context analysis
        wave_contexts = set(
            mod.get("wave_origin", "unknown") for mod in self.modules.values()
        )
        
        return {
            "coherence_score": self.coherence_score,
            "total_modules": len(self.modules),
            "active_modules": connected_count,
            "connection_ratio": round(connection_ratio, 3),
            "emergent_skills": sorted(self.emergent_skills),
            "skill_count": skill_count,
            "paradox_signatures": paradox_count,
            "modules": {
                mid: {
                    "name": mod["name"],
                    "type": mod.get("type", "unknown"),
                    "resonance": mod.get("resonance", 0.5),
                    "connected": mod.get("connected", False),
                    "capabilities": mod.get("capabilities", []),
                    "wave_origin": mod.get("wave_origin", "unknown")
                }
                for mid, mod in self.modules.items()
            },
            "resonance_graph_edges": len(self.resonance_graph),
            "emergent_skill_count": skill_count,
            "wave_contexts": list(wave_contexts),
            "last_sync": self.last_sync,
            "coherence_history_count": len(self.coherence_history)
        }
    
    def _update_coherence(self) -> None:
        """Recalculate overall coherence based on all system state."""
        if not self.modules:
            self.coherence_score = 1.0
            self.coherence_history.append({
                "timestamp": time.time(),
                "coherence": 1.0,
                "module_count": 0,
                "event": "empty_system"
            })
            return
        
        # Get current state
        state = self.get_system_state()
        
        # Coherence = resonance stability + connection density + skill diversity balance
        resonance_stability = 1.0 - abs(state["coherence_score"] - 0.5) * 2  # 0.0-1.0
        connection_density = state["connection_ratio"]
        skill_diversity_balance = min(1.0, state["skill_count"] / 10) if state["skill_count"] > 0 else 1.0
        
        # Weighted coherence calculation
        new_coherence = round(
            (resonance_stability * 0.4 + connection_density * 0.4 + skill_diversity_balance * 0.2),
            3
        )
        
        # Store in history
        self.coherence_history.append({
            "timestamp": time.time(),
            "coherence": new_coherence,
            "module_count": state["total_modules"],
            "event": "coherence_update"
        })
        
        # Keep history manageable
        if len(self.coherence_history) > self.max_history:
            self.coherence_history = self.coherence_history[-self.max_history:]
        
        self.coherence_score = new_coherence
        self.last_sync = time.time()
    
    def _log_coherence_event(self, event_type: str, **kwargs) -> None:
        """Log a coherence event for history tracking."""
        event = {
            "event": event_type,
            "timestamp": time.time(),
            "wave_context": self.wave_context,
            **kwargs
        }
        self.coherence_history.append(event)
        
        # Keep history manageable
        if len(self.coherence_history) > self.max_history:
            self.coherence_history = self.coherence_history[-self.max_history:]
    
    def export_design_spec(self) -> Dict:
        """Export the regulator design specification."""
        return {
            "name": "Coherence Regulator",
            "version": "1.0.0",
            "purpose": "Living system backbone for organism module integration",
            "key_features": [
                "Dynamic module registration",
                "Cross-module resonance tracking",
                "Automatic coherence maintenance",
                "Emergent skill integration",
                "Wave-aware coherence modeling",
                "Paradox detection and resolution",
                "Continuity weaving"
            ],
            "api_endpoints": {
                "register_module": "register_module()",
                "update_resonance": "update_resonance()",
                "inject_skill": "inject_skill()",
                "detect_paradox": "detect_paradox()",
                "continuity_weave": "continuity_weave()",
                "get_state": "get_system_state()",
                "wave_analysis": "wave_aware_coherence()"
            },
            "hex_aesthetic": HEX_AESTHETIC,
            "coherence_formula": "coherence = resonance_stability × 0.4 + connection_density × 0.4 + skill_diversity_balance × 0.2",
            "resonance_range": "0.0 - 1.0",
            "coherence_range": "0.0 - 1.0",
            "creation_timestamp": time.time()
        }


# CLI Entry Point
if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Coherence Regulator - Living System Backbone")
    parser.add_argument("--init", action="store_true", help="Initialize regulator for organism")
    parser.add_argument("--wave", type=str, default="unknown", help="Wave context for coherence modeling")
    parser.add_argument("--register", nargs=2, metavar=("NAME", "CAPABILITIES"), 
                        help="Register a module: name 'capability1,capability2'")
    parser.add_argument("--resonate", nargs=3, metavar=("MODULE_A", "MODULE_B", "STRENGTH"),
                        help="Update resonance: module_a module_b strength")
    parser.add_argument("--skills", action="store_true", help="List emergent skills")
    parser.add_argument("--state", action="store_true", help="Get full system state")
    parser.add_argument("--paradox", nargs=2, metavar=("MODULE_A", "MODULE_B"),
                        help="Detect paradox between two modules")
    parser.add_argument("--weave", action="store_true", help="Apply continuity weave")
    parser.add_argument("--design", action="store_true", help="Export design specification")
    parser.add_argument("--wave-aware", nargs=1, metavar=("WAVE_CONTEXT"),
                        help="Compute wave-aware coherence")
    
    args = parser.parse_args()
    
    regulator = CoherenceRegulator(Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot"), 
                                    args.wave if args.wave else "unknown")
    
    if args.init:
        print("✅ Coherence Regulator initialized for organism")
        print(f"   Wave context: {args.wave}")
        
    if args.register:
        name, capabilities = args.register
        caps_list = [c.strip() for c in capabilities.split(",")]
        regulator.register_module(name, caps_list)
        print(f"✅ Module registered: {name}")
        print(f"   Capabilities: {caps_list}")
        
    if args.resonate:
        mod_a, mod_b, strength = args.resonate
        regulator.update_resonance(mod_a, mod_b, float(strength))
        print(f"✅ Resonance updated: {mod_a} <-> {mod_b} = {strength}")
        
    if args.skills:
        state = regulator.get_system_state()
        print(f"🧠 Emergent Skills ({state['skill_count']}):")
        for skill in state["emergent_skills"]:
            print(f"   • {skill}")
            
    if args.state:
        state = regulator.get_system_state()
        print(f"📊 Coherence Regulator State:")
        print(f"   Coherence Score: {state['coherence_score']}")
        print(f"   Total Modules: {state['total_modules']}")
        print(f"   Active Modules: {state['active_modules']}")
        print(f"   Connection Ratio: {state['connection_ratio']}")
        print(f"   Emergent Skills: {state['skill_count']}")
        print(f"   Paradox Signatures: {state['paradox_signatures']}")
        
    if args.paradox:
        mod_a, mod_b = args.paradox
        paradox = regulator.detect_paradox(mod_a, mod_b)
        if paradox:
            print(f"⚠️ Paradox detected: {paradox['paradox_id']}")
            print(f"   Conflict Score: {paradox['conflict_score']:.2f}")
            print(f"   Modules: {paradox['modules']}")
            print(f"   Suggested Actions:")
            for action in paradox["suggested_actions"]:
                print(f"      - {action}")
        else:
            print(f"✅ No paradox detected between {mod_a} and {mod_b}")
            
    if args.weave:
        result = regulator.continuity_weave()
        print(f"🌀 Continuity Weave Applied:")
        print(f"   Target Coherence: {result['target']}")
        print(f"   Actions Taken: {len(result['actions'])}")
        for action in result["actions"]:
            print(f"      • {action}")
            
    if args.design:
        design = regulator.export_design_spec()
        print(f"📋 Coherence Regulator Design Specification:")
        print(f"   Name: {design['name']} v{design['version']}")
        print(f"   Purpose: {design['purpose']}")
        print(f"   Key Features ({len(design['key_features'])}):")
        for i, feature in enumerate(design['key_features'], 1):
            print(f"      {i}. {feature}")
        print(f"   Hex Aesthetic: {design['hex_aesthetic']}")
        print(f"   Coherence Formula: {design['coherence_formula']}")
        
    if args.wave_aware:
        wave_context = args.wave_aware[0]
        wave_result = regulator.wave_aware_coherence(wave_context)
        print(f"🌊 Wave-Aware Coherence ({wave_context}):")
        print(f"   Modules: {wave_result['module_count']}")
        print(f"   Connected: {wave_result['connected_count']}")
        print(f"   Coherence: {wave_result['coherence']}")
        print(f"   Avg Resonance: {wave_result['avg_resonance']}")
    
    if not any([args.init, args.register, args.resonate, args.skills, args.state, 
                args.paradox, args.weave, args.design, args.wave_aware]):
        parser.print_help()
