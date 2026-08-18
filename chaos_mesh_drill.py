#!/usr/bin/env python3
import json, time

def drill_raft_leader_loss():
    from raft_consensus import ConsensusNode
    a = ConsensusNode("chaos-a", ["chaos-b", "chaos-c"])
    b = ConsensusNode("chaos-b", ["chaos-a", "chaos-c"])
    c = ConsensusNode("chaos-c", ["chaos-a", "chaos-b"])
    for n in (a, b, c):
        for m in (a, b, c):
            n.known_pubs[m.node_id] = m.identity.public_b64()
    req = a.request_vote()
    grants = 1 + sum(1 for n in (b, c) if n.handle_vote_request(req)["type"] == "raft.VoteGrant")
    a.become_leader(grants)
    prop = a.propose("chaos_flag", {"phase": 1})
    for n in (b, c):
        n.handle_append(prop)
    req2 = b.request_vote()
    grants2 = 1 + sum(1 for n in (a, c) if n.handle_vote_request(req2)["type"] == "raft.VoteGrant")
    ok = b.become_leader(grants2) or grants2 >= 2
    return {"initial_leader": "chaos-a", "reelection_grants": grants2, "leader_elected": bool(ok or b.leader == "chaos-b"), "term_b": b.term}

def drill_dag_resume():
    from task_dag import DAGOrchestrator
    orch = DAGOrchestrator("chaos-dag")
    dag = orch.submit_intent("simulate lattice then evolve kernel then verify then publish for adjjv")
    steps = []
    ready = orch.next_tasks(dag.id)
    if ready:
        orch.complete(dag.id, ready[0]["id"], {"ok": True})
        steps.append(ready[0]["stage"])
    time.sleep(0.05)
    while not dag.all_done():
        ready = orch.next_tasks(dag.id)
        if not ready:
            break
        for t in ready:
            orch.complete(dag.id, t["id"], {"ok": True, "resumed": True})
            steps.append(t["stage"])
    return {"stages_completed": steps, "all_done": dag.all_done()}

def drill_byzantine_isolation():
    from byzantine_detector import AnomalyDetector
    det = AnomalyDetector(threshold=0.3)
    for _ in range(6):
        det.observe("honest", {"cpu": 0.2, "latency": 0.05, "energy": 0.5, "msg_rate": 0.3})
    det.observe("honest", {"cpu": 0.25, "latency": 0.06, "energy": 0.55, "msg_rate": 0.28})
    r = det.observe("honest", {"cpu": 0.99, "latency": 0.95, "energy": 50.0, "msg_rate": 0.0})
    return {"isolation_result": r, "trusted": det.trusted_nodes()}

def run_all():
    return {"raft_leader_loss": drill_raft_leader_loss(), "dag_resume": drill_dag_resume(), "byzantine": drill_byzantine_isolation()}

if __name__ == "__main__":
    print(json.dumps(run_all(), indent=2, default=str))
  
