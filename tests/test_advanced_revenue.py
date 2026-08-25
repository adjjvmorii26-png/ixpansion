from __future__ import annotations
"""Wave 98 — Advanced Revenue Streams Test Suite (44 tests).

Tests for: agent_rental, sponsored_experiments, simulation_as_a_service,
quantum_randomness, certification, digital_twin, alert_service.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Agent Rental ──────────────────────────────────────────────────

def test_agent_catalog_has_six():
    from api.agent_rental import AGENT_CATALOG
    assert len(AGENT_CATALOG) == 6
    ids = {a["id"] for a in AGENT_CATALOG}
    assert "scout_alpha" in ids
    assert "kintsugi_zeta" in ids

def test_available_agents():
    from api.agent_rental import AgentRentalSystem
    sys_ = AgentRentalSystem()
    avail = sys_.available_agents()
    assert len(avail) >= 5

def test_rent_agent():
    from api.agent_rental import AgentRentalSystem
    sys_ = AgentRentalSystem()
    result = sys_.rent("scout_alpha", "tester", 2)
    assert "rental_id" in result
    assert result["agent"] == "Scout Alpha"
    assert result["total_cost"] == 10.0
    sys_.release(result["rental_id"])

def test_rent_nonexistent_agent():
    from api.agent_rental import AgentRentalSystem
    sys_ = AgentRentalSystem()
    result = sys_.rent("ghost_agent", "tester", 1)
    assert "error" in result

def test_release_agent():
    from api.agent_rental import AgentRentalSystem
    sys_ = AgentRentalSystem()
    rental = sys_.rent("analyst_beta", "tester", 1)
    rid = rental["rental_id"]
    rel = sys_.release(rid)
    assert rel.get("released") or rel.get("status") == "released"

def test_agent_status():
    from api.agent_rental import AgentRentalSystem
    sys_ = AgentRentalSystem()
    rental = sys_.rent("sentinel_gamma", "tester", 24)
    status = sys_.status(rental["rental_id"])
    assert status.get("agent_id") == "sentinel_gamma"
    sys_.release(rental["rental_id"])

def test_rental_cost_calculation():
    from api.agent_rental import AgentRentalSystem
    sys_ = AgentRentalSystem()
    result = sys_.rent("kintsugi_zeta", "tester", 3)
    assert result["total_cost"] == 60.0
    sys_.release(result["rental_id"])


# ── Sponsored Experiments ─────────────────────────────────────────

def test_sponsorship_brief():
    from api.sponsored_experiments import SponsoredExperiments
    svc = SponsoredExperiments()
    brief = svc.submit_brief(
        "test_corp", "TestCorp Inc", "silver",
        description="Quantum bio research", domain="quantum"
    )
    assert brief["submitted"]
    assert brief["plan"] == "Silver Sponsor"

def test_approve_brief():
    from api.sponsored_experiments import SponsoredExperiments
    svc = SponsoredExperiments()
    brief = svc.submit_brief("sp", "SponsorCo", "bronze",
                             description="Test", domain="general")
    approved = svc.approve(brief["brief_id"])
    assert approved.get("approved")

def test_list_sponsorships():
    from api.sponsored_experiments import SponsoredExperiments
    svc = SponsoredExperiments()
    svc.submit_brief("sp2", "Co2", "gold", description="Gold test", domain="ecology")
    listings = svc.list_sponsorships()
    assert len(listings) >= 1

def test_plan_tiers():
    from api.sponsored_experiments import SPONSORSHIP_PLANS
    assert "bronze" in SPONSORSHIP_PLANS
    assert "platinum" in SPONSORSHIP_PLANS
    assert SPONSORSHIP_PLANS["platinum"]["experiments"] == -1


# ── Simulation as a Service ───────────────────────────────────────

def test_simulation_templates_exist():
    from api.simulation_as_a_service import SIMULATION_TEMPLATES
    assert "ecosystem_growth" in SIMULATION_TEMPLATES
    assert "quantum_experiment" in SIMULATION_TEMPLATES
    assert "code_archaeology" in SIMULATION_TEMPLATES
    assert "temporal_analysis" in SIMULATION_TEMPLATES

def test_run_simulation():
    from api.simulation_as_a_service import SimulationService
    svc = SimulationService()
    result = svc.run_simulation("ecosystem_growth", user="tester")
    assert "sim_id" in result
    assert result["template"] == "ecosystem_growth"
    assert "credits_charged" in result

def test_simulation_results():
    from api.simulation_as_a_service import SimulationService
    svc = SimulationService()
    run = svc.run_simulation("cosmic_mapping", user="tester")
    results = svc.get_results(run["sim_id"])
    assert "sim_id" in results
    assert results["sim_id"] == run["sim_id"]

def test_custom_params():
    from api.simulation_as_a_service import SimulationService
    svc = SimulationService()
    result = svc.run_simulation(
        "code_archaeology", custom_params={"depth": 3}, user="tester"
    )
    assert result["sim_id"]

def test_unknown_template():
    from api.simulation_as_a_service import SimulationService
    svc = SimulationService()
    result = svc.run_simulation("nonexistent_template")
    assert "error" in result


# ── Quantum Randomness ────────────────────────────────────────────

def test_generate_numbers():
    from api.quantum_randomness import QuantumRandomnessAPI
    api = QuantumRandomnessAPI()
    result = api.generate(count=10, min_val=1, max_val=50)
    assert result["count"] == 10
    assert len(result["numbers"]) == 10
    assert all(1 <= n <= 50 for n in result["numbers"])

def test_generate_integers():
    from api.quantum_randomness import QuantumRandomnessAPI
    api = QuantumRandomnessAPI()
    result = api.generate(count=5, min_val=0, max_val=100, precision=0)
    assert all(isinstance(n, int) for n in result["numbers"])

def test_generate_too_many():
    from api.quantum_randomness import QuantumRandomnessAPI
    api = QuantumRandomnessAPI()
    result = api.generate(count=10001)
    assert "error" in result

def test_generate_bytes():
    from api.quantum_randomness import QuantumRandomnessAPI
    api = QuantumRandomnessAPI()
    result = api.generate_bytes(64)
    assert len(result["bytes"]) == 128

def test_generate_uuid():
    from api.quantum_randomness import QuantumRandomnessAPI
    api = QuantumRandomnessAPI()
    uid = api.generate_uuid()
    assert len(uid) == 32
    assert uid != api.generate_uuid()

def test_generate_passphrase():
    from api.quantum_randomness import QuantumRandomnessAPI
    api = QuantumRandomnessAPI()
    phrase = api.generate_passphrase(4)
    parts = phrase.split("-")
    assert len(parts) == 4

def test_quantum_stats():
    from api.quantum_randomness import QuantumRandomnessAPI
    api = QuantumRandomnessAPI()
    api.generate(5)
    api.generate_bytes(32)
    stats = api.stats()
    assert stats["total_generations"] >= 1
    assert stats["total_bytes"] >= 32


# ── Certification ─────────────────────────────────────────────────

def test_enroll_explorer():
    from api.certification import CertificationProgram
    prog = CertificationProgram()
    result = prog.enroll("alice", "explorer")
    assert result.get("enrolled")
    assert result["path"] == "IXpansion Certified Explorer (ICE)"

def test_enroll_requires_prerequisite():
    from api.certification import CertificationProgram
    prog = CertificationProgram()
    result = prog.enroll("alice", "architect")
    assert "error" in result or result.get("prerequisite_required")

def test_take_exam():
    from api.certification import CertificationProgram
    prog = CertificationProgram()
    prog.enroll("bob", "explorer")
    result = prog.take_exam("bob", "explorer")
    assert "passed" in result or "score" in result

def test_verify_cert():
    from api.certification import CertificationProgram
    prog = CertificationProgram()
    result = prog.verify("fake_cert_id_123")
    assert result.get("valid") is False

def test_leaderboard():
    from api.certification import CertificationProgram
    prog = CertificationProgram()
    lb = prog.leaderboard(5)
    assert isinstance(lb, list)

def test_cert_paths():
    from api.certification import LEARNING_PATHS
    assert len(LEARNING_PATHS) == 3
    assert LEARNING_PATHS["explorer"]["level"] == 1
    assert LEARNING_PATHS["architect"]["level"] == 3


# ── Digital Twin ──────────────────────────────────────────────────

def test_create_twin():
    from api.digital_twin import DigitalTwinService
    svc = DigitalTwinService()
    twin = svc.create("my_api", "microservice", "tester")
    assert "twin_id" in twin
    assert twin["name"] == "my_api"

def test_mirror_twin():
    from api.digital_twin import DigitalTwinService
    svc = DigitalTwinService()
    twin = svc.create("svc", "service", "tester")
    mirrored = svc.mirror(twin["twin_id"], {"cpu": 45, "mem": 1024})
    assert mirrored.get("mirrored") or mirrored.get("synced")

def test_simulate_twin():
    from api.digital_twin import DigitalTwinService
    svc = DigitalTwinService()
    twin = svc.create("sim_test", "db", "tester")
    sim = svc.simulate(twin["twin_id"], "stress", ticks=5)
    assert "sim_id" in sim or sim.get("completed")

def test_twin_health():
    from api.digital_twin import DigitalTwinService
    svc = DigitalTwinService()
    twin = svc.create("health_check", "api", "tester")
    health = svc.health(twin["twin_id"])
    assert "health" in health or "status" in health

def test_list_twins():
    from api.digital_twin import DigitalTwinService
    svc = DigitalTwinService()
    svc.create("t1", "service", "user_x")
    svc.create("t2", "service", "user_x")
    twins = svc.list_twins("user_x")
    assert len(twins) >= 2

def test_list_twins_by_owner():
    from api.digital_twin import DigitalTwinService
    svc = DigitalTwinService()
    svc.create("own1", "api", "owner_a")
    svc.create("own2", "api", "owner_b")
    a_twins = svc.list_twins("owner_a")
    assert all(t.get("owner") == "owner_a" for t in a_twins)


# ── Alert Service ─────────────────────────────────────────────────

def test_alert_channels():
    from api.alert_service import ALERT_CHANNELS
    assert "slack" in ALERT_CHANNELS
    assert "discord" in ALERT_CHANNELS
    assert "webhook" in ALERT_CHANNELS
    assert "email" in ALERT_CHANNELS

def test_subscribe():
    from api.alert_service import AlertService
    svc = AlertService()
    result = svc.subscribe("user1", "slack")
    assert result.get("subscribed")
    assert result["monthly_cost"] == 9

def test_subscribe_unknown_channel():
    from api.alert_service import AlertService
    svc = AlertService()
    result = svc.subscribe("user1", "smoke_signal")
    assert "error" in result

def test_configure_rules():
    from api.alert_service import AlertService
    svc = AlertService()
    svc.subscribe("user1", "email")
    result = svc.configure_rules("user1", ["cpu_high", "error_spike"])
    assert result["configured"]
    assert len(result["rules"]) == 2

def test_fire_alert():
    from api.alert_service import AlertService
    svc = AlertService()
    svc.subscribe("user1", "slack")
    fired = svc.fire_alert("error_spike", {"rate": 8.5})
    assert fired["alert"]["rule"] == "error_spike"
    assert fired["delivered_to"] >= 1

def test_alert_history():
    from api.alert_service import AlertService
    svc = AlertService()
    svc.fire_alert("anomaly_detected", {"info": "test"})
    history = svc.history(5)
    assert len(history) >= 1

def test_active_alerts():
    from api.alert_service import AlertService
    svc = AlertService()
    svc.fire_alert("cpu_high", {"pct": 95})
    active = svc.list_active()
    assert len(active) >= 1

def test_alert_rules():
    from api.alert_service import ALERT_RULES
    assert len(ALERT_RULES) == 8
    assert ALERT_RULES["error_spike"]["severity"] == "critical"


# ── Handler smoke tests ───────────────────────────────────────────

def test_agent_rental_handler():
    from api.agent_rental import handler
    result = handler({}, {})
    assert isinstance(result, list)

def test_sponsored_handler():
    from api.sponsored_experiments import handler
    result = handler({}, {})
    assert isinstance(result, dict)

def test_simulation_handler():
    from api.simulation_as_a_service import handler
    result = handler({}, {})
    assert isinstance(result, dict)

def test_quantum_handler():
    from api.quantum_randomness import handler
    result = handler({}, {})
    assert isinstance(result, dict)

def test_certification_handler():
    from api.certification import handler
    result = handler({}, {})
    assert isinstance(result, dict)

def test_twin_handler():
    from api.digital_twin import handler
    result = handler({}, {})
    assert isinstance(result, list)

def test_alert_handler():
    from api.alert_service import handler
    result = handler({}, {})
    assert isinstance(result, dict)
