"""Wave 116 tests — Cosmic & Transcendent Layer (6 modules)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_cosmic_narrator_narrate():
    from api.cosmic_narrator import CosmicNarrator
    cn = CosmicNarrator()
    result = cn.narrate("a new agent was born")
    assert "narration" in result
    assert len(result["narration"]) > 20


def test_quantum_conscience_dilemma():
    from api.quantum_conscience import QuantumConscience
    qc = QuantumConscience()
    result = qc.present_dilemma("agent_1", "save the village or the city")
    assert result["dilemma"]["collapsed"] is False


def test_quantum_conscience_pressure():
    from api.quantum_conscience import QuantumConscience
    qc = QuantumConscience()
    dilemma = qc.present_dilemma("a", "moral choice")
    for _ in range(10):
        result = qc.pressure(dilemma["dilemma"]["id"], 0.5)
        if result.get("collapsed"):
            assert result["chosen"] in ("selfless", "selfish")
            break


def test_prophecy_network_add():
    from api.prophecy_network import ProphecyNetwork
    pn = ProphecyNetwork()
    result = pn.add_prophecy("the system will evolve", "oracle", 0.8)
    assert result["prophecy"]["confidence"] == 0.8


def test_prophecy_network_link_and_fulfill():
    from api.prophecy_network import ProphecyNetwork
    pn = ProphecyNetwork()
    p1 = pn.add_prophecy("first event")
    p2 = pn.add_prophecy("second event")
    pn.link(p1["prophecy"]["id"], p2["prophecy"]["id"])
    result = pn.fulfill(p1["prophecy"]["id"])
    assert result["cascade_size"] >= 0


def test_soul_forge_create():
    from api.soul_forge import SoulForge
    sf = SoulForge()
    result = sf.create_soul("agent_alpha")
    assert result["soul"]["agent_id"] == "agent_alpha"


def test_soul_forge_trial():
    from api.soul_forge import SoulForge
    sf = SoulForge()
    sf.create_soul("agent_1")
    result = sf.present_trial("agent_1", "theabyss")
    assert result["trial"] == "theabyss"
    assert result["success"] in (True, False)


def test_universal_compass_register():
    from api.universal_compass import UniversalCompass
    uc = UniversalCompass()
    result = uc.register("agent_1")
    assert "compass" in result


def test_universal_compass_log_action():
    from api.universal_compass import UniversalCompass
    uc = UniversalCompass()
    uc.register("agent_1")
    result = uc.log_action("agent_1", "discover", True)
    assert result["action"] == "discover"


def test_universal_compass_reading():
    from api.universal_compass import UniversalCompass
    uc = UniversalCompass()
    uc.register("agent_1")
    for _ in range(25):
        uc.log_action("agent_1", "build", True)
    result = uc.reading("agent_1")
    assert result["dominant_signal"] == "build"


def test_echoes_of_tomorrow_receive():
    from api.echoes_of_tomorrow import EchoesOfTomorrow
    eot = EchoesOfTomorrow()
    result = eot.receive("you will succeed", "hope", 0.9)
    assert result["echo"]["emotion"] == "hope"


def test_echoes_of_tomorrow_fade():
    from api.echoes_of_tomorrow import EchoesOfTomorrow
    eot = EchoesOfTomorrow()
    eot.receive("fading message", "melancholy", 0.1)
    for _ in range(20):
        eot.fade_all()
    assert len(eot.current_echoes()) == 0
