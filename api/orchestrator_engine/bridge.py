"""Bridge between organism_orchestrator and ixpansion core."""

from api.orchestrator_engine.orchestrator import OrganismOrchestrator
from api.persona import create_persona, AgentPersona

# Global orchestrator instance
orchestrator = OrganismOrchestrator()

def init_orchestrator(organism_id="ixpansion"):
    """Initialize the orchestrator for the ixpansion organism."""
    global orchestrator
    orchestrator.organism_id = organism_id
    print(f"✓ Organism orchestrator initialized for {organism_id}")
    return orchestrator

def evolve_wave(wave_id, changes):
    """Evolve the organism through a wave."""
    return orchestrator.evolve_wave(wave_id, changes)

def evolve_persona(agent_id, updates):
    """Evolve an agent's persona."""
    return orchestrator.evolve_persona(agent_id, updates)

def get_status():
    """Get current organism status."""
    return orchestrator.get_status()
