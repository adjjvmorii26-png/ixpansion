"""
aegis — Guard organ for IXpansion organism.

Components:
  - tripwire_canary.py: Honey-token detection & breach response
  - aegis_dashboard.py: FastAPI control plane (WebSocket real-time)
  - test_triad_integration.py: Sentinel + Tripwire + VSA integration tests
  - docker-compose.yml: Redis bus + identity + dashboard service stack

Originally developed in aegis-workspace codespace. Merged into organism core.
"""
from .tripwire_canary import TripwireCanaryEngine
