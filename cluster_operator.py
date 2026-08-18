#!/usr/bin/env python3
"""
Lightweight Cluster Operator (K8s/Nomad-style)
Raft-aware scaling decisions + manifest generation for edge workers.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

OUT = Path("/home/workdir/artifacts/cluster_manifests")
OUT.mkdir(exist_ok=True)

class ClusterOperator:
    def __init__(self, min_workers: int = 1, max_workers: int = 8, scale_up_load: float = 0.7):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.scale_up_load = scale_up_load
        self.desired = min_workers
        self.history: List[dict] = []

    def observe(self, avg_cpu: float, queue_depth: int, active_workers: int) -> dict:
        decision = "hold"
        if avg_cpu > self.scale_up_load or queue_depth > active_workers * 2:
            if active_workers < self.max_workers:
                self.desired = min(self.max_workers, active_workers + 1)
                decision = "scale_up"
        elif avg_cpu < 0.2 and queue_depth == 0 and active_workers > self.min_workers:
            self.desired = max(self.min_workers, active_workers - 1)
            decision = "scale_down"
        else:
            self.desired = max(self.min_workers, active_workers)
        rec = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
            "desired_workers": self.desired,
            "avg_cpu": avg_cpu,
            "queue_depth": queue_depth,
            "active_workers": active_workers,
        }
        self.history.append(rec)
        return rec

    def render_k8s_deployment(self, image: str = "swarm:latest", replicas: Optional[int] = None) -> dict:
        r = replicas if replicas is not None else self.desired
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "swarm-worker", "labels": {"app": "ixpansion-swarm"}},
            "spec": {
                "replicas": r,
                "selector": {"matchLabels": {"app": "swarm-worker"}},
                "template": {
                    "metadata": {"labels": {"app": "swarm-worker"}},
                    "spec": {
                        "containers": [{
                            "name": "worker",
                            "image": image,
                            "env": [
                                {"name": "SWARM_ROLE", "value": "worker"},
                                {"name": "SWARM_HUB", "value": "ws://swarm-hub:8765"},
                                {"name": "SWARM_TOKEN", "valueFrom": {"secretKeyRef": {"name": "swarm-token", "key": "token"}}},
                            ],
                            "resources": {
                                "limits": {"memory": "512Mi", "cpu": "500m"},
                                "requests": {"memory": "128Mi", "cpu": "100m"},
                            },
                        }]
                    },
                },
            },
        }
        path = OUT / "worker-deployment.json"
        path.write_text(json.dumps(manifest, indent=2))
        return {"path": str(path), "replicas": r}

    def render_nomad_job(self, count: Optional[int] = None) -> dict:
        c = count if count is not None else self.desired
        job = {
            "Job": {
                "ID": "swarm-worker",
                "Name": "swarm-worker",
                "Type": "service",
                "Datacenters": ["dc1"],
                "TaskGroups": [{
                    "Name": "workers",
                    "Count": c,
                    "Tasks": [{
                        "Name": "worker",
                        "Driver": "docker",
                        "Config": {"image": "swarm:latest"},
                        "Env": {"SWARM_ROLE": "worker", "SWARM_HUB": "ws://hub.service.consul:8765"},
                    }],
                }],
            }
        }
        path = OUT / "worker-nomad.json"
        path.write_text(json.dumps(job, indent=2))
        return {"path": str(path), "count": c}

if __name__ == "__main__":
    op = ClusterOperator()
    print(op.observe(0.85, 10, 2))
    print(op.render_k8s_deployment())
    print(op.render_nomad_job())
                                   
