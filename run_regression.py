#!/usr/bin/env python3
"""IXPANSION regression suite — happy path, faults, CRDT properties, arch drift."""
from __future__ import annotations
import json, random, traceback
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("content_output/regression")
OUT.mkdir(parents=True, exist_ok=True)

def run():
    results = []
    def check(name, fn):
        try:
            data = fn()
            results.append({"name": name, "ok": True, **(data if isinstance(data, dict) else {"detail": data})})
            print(f"  PASS {name}")
        except Exception as e:
            results.append({"name": name, "ok": False, "error": str(e), "trace": traceback.format_exc()[-400:]})
            print(f"  FAIL {name}: {e}")

    def t_raft():
        from raft_consensus import simulate_election_and_commit
        r = simulate_election_and_commit()
        assert r.get("leader") and r.get("quorum", 0) >= 2
        return {"leader": r["leader"], "quorum": r["quorum"]}

    def t_raft_partition():
        from raft_consensus import ConsensusNode
        a = ConsensusNode("p-a", ["p-b", "p-c"])
        b = ConsensusNode("p-b", ["p-a", "p-c"])
        c = ConsensusNode("p-c", ["p-a", "p-b"])
        for n in (a, b, c):
            for m in (a, b, c):
                n.known_pubs[m.node_id] = m.identity.public_b64()
        req = a.request_vote()
        grants = 1 + sum(1 for n in (b, c) if n.handle_vote_request(req)["type"] == "raft.VoteGrant")
        assert a.become_leader(grants)
        # partition: only B starts election (A "isolated")
        req2 = b.request_vote()
        # C can vote; A may reject or grant depending on term
        grants2 = 1
        for n in (c,):
            if n.handle_vote_request(req2)["type"] == "raft.VoteGrant":
                grants2 += 1
        elected = b.become_leader(grants2) or grants2 >= 2
        return {"partition_election_grants": grants2, "progress": elected or b.term >= 1}

    def t_compiler():
        from mesh_compiler import compile_intent, negative_test_suite
        c = compile_intent("simulate lattice N=8 and verify transcript")
        neg = negative_test_suite()
        assert neg["receipt_forgery"]["dropped"]
        assert neg["gas_exhaustion"]["trapped"]
        return {"compile_ok": c.get("ok"), "negatives_ok": True}

    def t_malformed_proof():
        from task_verifiability import verify_transcript
        bad = {"task_id": "x", "constraint": "c", "steps": [], "result_commit": "0"*64,
               "result": {"final_energy": 1}, "proof": {"type": "transcript_v1", "root": "deadbeef"}}
        ok, reason = verify_transcript(bad)
        assert not ok
        return {"rejected": True, "reason": reason}

    def t_genetic():
        from genetic_sandbox import evaluate_expr
        fit_c, _ = evaluate_expr("(0.02 - 0.02)")
        fit_a, _ = evaluate_expr("(c * 0.5 + neigh * 0.5)")
        assert fit_c > fit_a
        return {"collapse_worse": True}

    def t_dag():
        from task_dag import DAGOrchestrator
        o = DAGOrchestrator("reg")
        d = o.submit_intent("simulate lattice evolve kernel verify publish adjjv")
        steps = []
        while not d.all_done():
            for t in o.next_tasks(d.id):
                o.complete(d.id, t["id"], {"ok": True})
                steps.append(t["stage"])
        assert d.all_done()
        return {"steps": steps}

    def t_verify():
        from spatial_shard import run_adaptive
        from task_verifiability import prove_lattice_run, verify_transcript
        lat = run_adaptive(n=10, steps=6, seed=0.2, worker_loads={"a": 0.3})
        p = prove_lattice_run("reg", {"n": 10}, lat)
        ok, _ = verify_transcript(p)
        assert ok
        return {"verified": ok}

    def t_reputation_ema():
        from reputation_ledger import ReputationLedger
        r = ReputationLedger(half_life_events=5)
        r.stake("n1", 1)
        for _ in range(4):
            r.record_success("n1", weight=0.5)
        hi = r.trust_weight("n1")
        for _ in range(6):
            r.record_failure("n1", weight=0.4)
        lo = r.trust_weight("n1")
        assert lo < hi
        return {"decayed": True, "hi": hi, "lo": lo}

    def t_crdt_property():
        """Random merge orders must converge (LWW + OR-Set)."""
        from swarm_crdt import CRDTBlackboard
        def once():
            nodes = [CRDTBlackboard(f"n{i}") for i in range(3)]
            ops = []
            for i in range(12):
                n = random.choice(nodes)
                if random.random() < 0.7:
                    k = random.choice(["a", "b", "c"])
                    n.set(k, random.randint(0, 50))
                    ops.append(("set", n.node_id, k))
                else:
                    n.add_agent(f"agent-{random.randint(0, 3)}")
            # random pairwise merges
            order = [(i, j) for i in range(3) for j in range(3) if i != j]
            random.shuffle(order)
            for i, j in order:
                nodes[i].merge(nodes[j])
            # full mesh
            for _ in range(2):
                for i in range(3):
                    for j in range(3):
                        if i != j:
                            nodes[i].merge(nodes[j])
            keys = set()
            for n in nodes:
                keys |= set(n.registers.keys())
            for k in keys:
                vals = [n.get(k) for n in nodes]
                assert all(v == vals[0] for v in vals), (k, vals)
            agents = [frozenset(n.agents.values()) for n in nodes]
            assert all(a == agents[0] for a in agents)
            return True
        for _ in range(5):
            once()
        return {"trials": 5, "converged": True}

    def t_vsa_capacity():
        from vsa_memory import VSAMemory
        m = VSAMemory()
        for i in range(20):
            m.atom(f"tok_{i}")
        h = m.capacity_health()
        assert "mean_abs_cosine" in h
        return h

    def t_arch_drift():
        from arch_snapshot import snapshot
        live = snapshot()
        path = Path("content_output/architecture_snapshot.json")
        if path.exists():
            prev = json.loads(path.read_text())
            prev_count = prev.get("python_modules", 0)
            live_count = live.get("python_modules", 0)
            # rewrite snapshot is ok; flag if module count dropped sharply
            drift = live_count - prev_count
            # refresh file already done by snapshot()
            return {"prev": prev_count, "live": live_count, "delta": drift, "flag": drift < -5}
        return {"live": live.get("python_modules"), "flag": False}

    def t_grok_safety_gate():
        """Grok bridge must not dispatch without key; capability path fails closed."""
        from grok_swarm_client import GrokClient, execute_grok_capability
        c = GrokClient()
        if not c.available:
            r = execute_grok_capability("synthesize", {"title": "x"})
            assert "error" in r or r.get("offline") or not r.get("ok", True)
            return {"enforced": True, "mode": "no_key"}
        # with key, still only allow mapped capabilities
        r = execute_grok_capability("not_a_real_cap", {})
        assert "error" in r
        return {"enforced": True, "mode": "mapped_only"}

    
    def t_frame_budget():
        from frame_budget_harness import run as fb
        r = fb(steps=100, dim=128, n=16)
        assert r["within_budget"]
        return {"worst_ms": r["worst_ms"], "avg_ms": r["avg_ms"]}

    def t_breakers():
        from breaker_smoke import run as br
        return br()

    def t_buffer_contract():
        from buffer_contract import BufferContract, demo_tick
        bc = BufferContract(dim=64, lattice_n=8, n_slots=3)
        demo_tick(bc, 5)
        h = bc.orthogonality_health()
        assert "mean_abs_cosine" in h
        return {"hash": bc.state_hash(), "ortho": h["status"]}

    def t_epoch_diff():
        from epoch_diff_tool import two_runs
        r = two_runs(steps=50, interval=25)
        assert r["same_seed_ok"]
        return r


    print("IXPANSION regression")
    tests = [
        ("raft", t_raft),
        ("raft_partition", t_raft_partition),
        ("compiler", t_compiler),
        ("malformed_proof", t_malformed_proof),
        ("genetic_penalty", t_genetic),
        ("dag", t_dag),
        ("zk_transcript", t_verify),
        ("reputation_ema", t_reputation_ema),
        ("crdt_property", t_crdt_property),
        ("vsa_capacity", t_vsa_capacity),
        ("arch_drift", t_arch_drift),
        ("grok_safety_gate", t_grok_safety_gate),
        ("frame_budget", t_frame_budget),
        ("breakers", t_breakers),
        ("buffer_contract", t_buffer_contract),
        ("epoch_diff", t_epoch_diff),
    ]
    for name, fn in tests:
        check(name, fn)
    passed = sum(1 for r in results if r["ok"])
    report = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "total": len(results),
        "results": results,
    }
    path = OUT / f"regression_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(report, indent=2, default=str))
    print(f"{passed}/{len(results)} → {path}")
    return report

if __name__ == "__main__":
    r = run()
    raise SystemExit(0 if r["passed"] == r["total"] else 1)
      
