"""Organism Orchestrator - coordinates evolution across all dimensions."""

from typing import Dict, List, Any, Optional
import time
import json

class OrganismOrchestrator:
    """Orchestrates the evolution of the organism across multiple dimensions.
    
    Responsibilities:
    - Coordinate wave evolution
    - Manage module lifecycle
    - Maintain coherence across subsystems
    - Orchestrate persona evolution
    - Coordinate dream and memory integration
    """
    
    def __init__(self, organism_id: str = "organism_orchestrator"):
        self.organism_id = organism_id
        self.waves = []
        self.modules = {}
        self.personas = {}
        self.coherence_score = 1.0
        self.creation_time = time.time()
        self.dimension_metrics = {}
        
    def register_module(self, module_id: str, module_data: dict):
        """Register a new module in the organism."""
        self.modules[module_id] = module_data
        self.coherence_score = max(0.0, self.coherence_score - 0.01)
        
    def unregister_module(self, module_id: str):
        """Remove a module from the organism."""
        if module_id in self.modules:
            del self.modules[module_id]
            self.coherence_score = min(1.0, self.coherence_score + 0.01)
    
    def evolve_wave(self, wave_id: str, changes: dict) -> dict:
        """Evolve the organism through a wave."""
        # Apply changes
        for change_type, change_data in changes.items():
            if change_type == "add_module":
                self.register_module(change_data.get("id", "unknown"), change_data)
            elif change_type == "update_module":
                if change_data.get("id") in self.modules:
                    self.modules[change_data["id"]].update(change_data.get("data", {}))
            elif change_type == "remove_module":
                self.unregister_module(change_data.get("id", "unknown"))
        
        # Generate wave report
        report = {
            "wave_id": wave_id,
            "modules_after": len(self.modules),
            "coherence_before": self.coherence_score,
            "changes_applied": len(changes),
            "timestamp": time.time(),
            "organism_id": self.organism_id,
        }
        
        # Update coherence after wave
        self.coherence_score = max(0.1, self.coherence_score + 0.05)
        report["coherence_after"] = self.coherence_score
        
        self.waves.append(report)
        return report
    
    def evolve_persona(self, agent_id: str, updates: dict) -> dict:
        """Evolve an agent's persona."""
        if agent_id not in self.personas:
            self.personas[agent_id] = {
                "curiosity": 0.5,
                "creativity": 0.5,
                "risk_aversion": 0.5,
                "cooperation": 0.5,
                "exploration": 0.5,
            }
        
        persona = self.personas[agent_id]
        for key, value in updates.items():
            if key in persona:
                persona[key] = min(1.0, max(0.0, value))
        
        return persona
    
    def get_status(self) -> dict:
        """Get current organism status."""
        return {
            "organism_id": self.organism_id,
            "total_modules": len(self.modules),
            "total_waves": len(self.waves),
            "total_personas": len(self.personas),
            "coherence_score": round(self.coherence_score, 4),
            "dimension_metrics": self.dimension_metrics,
        }
