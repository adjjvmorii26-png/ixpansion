"""Dependency-free 1.3 federation demo components.

This module is a deterministic simulator for local testing. It does not open
network sockets, execute shell commands, or claim production federation.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from lattice_stack import Machine, build_lattice_stack


Fitness = Callable[[List[float]], float]


def sphere(values: List[float]) -> float:
    return sum(value * value for value in values)


@dataclass
class PSOConfig:
    dim: int = 3
    n_particles: int = 8
    iters: int = 12
    seed: int = 9


@dataclass
class FederatedConfig:
    n_clusters: int = 3
    islands_per_cluster: int = 2
    rounds: int = 2
    pso: PSOConfig = field(default_factory=PSOConfig)


@dataclass
class Federate:
    cluster_id: str
    trust_to: Dict[str, float]


class FederateTransport:
    def __init__(self, loss_rate: float = 0.0, seed: int = 0):
        if not 0 <= loss_rate <= 1:
            raise ValueError("loss_rate must be between 0 and 1")
        self.loss_rate = loss_rate
        self.random = random.Random(seed)
        self.queues: Dict[str, List[dict]] = {}
        self.sent = 0
        self.dropped = 0

    def send(self, sender: str, recipient: str, payload: dict) -> bool:
        self.sent += 1
        if self.random.random() < self.loss_rate:
            self.dropped += 1
            return False
        self.queues.setdefault(recipient, []).append(
            {"sender": sender, "payload": payload}
        )
        return True

    def recv(self, recipient: str) -> List[dict]:
        return self.queues.pop(recipient, [])

    def snapshot(self) -> dict:
        return {"sent": self.sent, "dropped": self.dropped, "queued": sum(map(len, self.queues.values()))}


class WANParticleMigrator:
    def __init__(self, transport: FederateTransport):
        self.transport = transport
        self.history: List[dict] = []

    def export_elites(self, sender: str, population: List[List[float]], fitnesses: List[float], k: int = 2) -> dict:
        if len(population) != len(fitnesses):
            raise ValueError("population and fitnesses must have equal lengths")
        indexes = sorted(range(len(population)), key=fitnesses.__getitem__)[: max(0, k)]
        return {"sender": sender, "elites": [{"x": population[i], "fitness": fitnesses[i]} for i in indexes]}

    def send(self, bundle: dict, recipient: str) -> bool:
        delivered = self.transport.send(bundle["sender"], recipient, {"elites": bundle["elites"]})
        self.history.append({"sender": bundle["sender"], "recipient": recipient, "delivered": delivered})
        return delivered


class VSAScratchpad:
    def __init__(self, dimensions: int = 64):
        self.dimensions = dimensions
        self.frames: List[dict] = []

    def store(self, frame: dict) -> None:
        self.frames.append(frame)

    def snapshot(self) -> dict:
        return {"dimensions": self.dimensions, "frames": len(self.frames)}


def encode_gbest(cluster_id: str, best_x: List[float], fitness: float, pad: VSAScratchpad) -> dict:
    frame = {"cluster_id": cluster_id, "best_x": list(best_x), "fitness": fitness}
    pad.store(frame)
    return frame


def ship_gbest(network: Dict[Tuple[str, str], List[dict]], sender: str, recipient: str, best_x: List[float], fitness: float = 0.0) -> None:
    network.setdefault((sender, recipient), []).append({"best_x": list(best_x), "fitness": fitness})


def recv_gbest_frames(network: Dict[Tuple[str, str], List[dict]], recipient: str) -> List[dict]:
    frames = []
    for (sender, target), values in network.items():
        if target == recipient:
            frames.extend(values)
    return frames


def rank_clusters_by_carbon(
    cluster_ids: Iterable[str],
    green_scores: Dict[str, float],
    default: float = 0.5,
) -> List[Tuple[str, float]]:
    """Rank clusters from greenest to least green."""
    return sorted(
        ((cluster, green_scores.get(cluster, default)) for cluster in cluster_ids),
        key=lambda item: -item[1],
    )


def select_primary_federate(
    cluster_ids: Iterable[str],
    green_scores: Dict[str, float],
    min_score: float = 0.0,
) -> Optional[str]:
    ranked = rank_clusters_by_carbon(cluster_ids, green_scores)
    for cluster, score in ranked:
        if score >= min_score:
            return cluster
    return ranked[0][0] if ranked else None


def carbon_aware_weights(green_scores: Dict[str, float]) -> Dict[str, float]:
    """Normalize carbon scores into trust-like federation weights."""
    if not green_scores:
        return {}
    low = min(green_scores.values())
    high = max(green_scores.values())
    span = (high - low) or 1.0
    return {
        cluster: 0.2 + 0.8 * ((score - low) / span)
        for cluster, score in green_scores.items()
    }


def _run_pso(fitness: Fitness, config: PSOConfig) -> Tuple[List[float], float]:
    randomizer = random.Random(config.seed)
    population = [[randomizer.uniform(-1, 1) for _ in range(config.dim)] for _ in range(config.n_particles)]
    best_x = min(population, key=fitness)
    best_fitness = fitness(best_x)
    for _ in range(config.iters):
        for particle in population:
            for index in range(config.dim):
                particle[index] = (particle[index] + best_x[index]) / 2
            score = fitness(particle)
            if score < best_fitness:
                best_x, best_fitness = list(particle), score
    return best_x, best_fitness


def federated_island_pso(fitness: Fitness, config: FederatedConfig, clusters: Dict[str, Federate]) -> dict:
    results = {
        cluster_id: _run_pso(
            fitness,
            PSOConfig(
                dim=config.pso.dim,
                n_particles=config.pso.n_particles,
                iters=config.pso.iters,
                seed=config.pso.seed + index,
            ),
        )
        for index, cluster_id in enumerate(clusters)
    }
    winner = min(results, key=lambda cluster: results[cluster][1])
    return {"winner_cluster": winner, "best_x": results[winner][0], "best_fitness": results[winner][1], "clusters": {key: {"best_fitness": value[1]} for key, value in results.items()}}


def run_1_3_stack(fitness: Optional[Fitness] = None, green_scores: Optional[Dict[str, float]] = None, n_clusters: int = 3) -> dict:
    fit = fitness or sphere
    scores = green_scores or {f"cluster-{i}": 0.5 + 0.2 * i for i in range(n_clusters)}
    primary = select_primary_federate(scores, scores) or "cluster-0"
    weights = carbon_aware_weights(scores)
    clusters = {
        cluster: Federate(cluster, {other: weights.get(other, 0.4) for other in scores if other != cluster})
        for cluster in scores
    }
    result = federated_island_pso(fit, FederatedConfig(n_clusters=n_clusters), clusters)
    transport = FederateTransport(loss_rate=0.05, seed=9)
    wan = WANParticleMigrator(transport)
    pad = VSAScratchpad(64)
    network: Dict[Tuple[str, str], List[dict]] = {}
    winner = result["winner_cluster"]
    best_x = result["best_x"]
    encode_gbest(winner, best_x, result["best_fitness"], pad)
    for recipient in scores:
        if recipient != winner:
            transport.send(winner, recipient, {"best_x": best_x, "fitness": result["best_fitness"]})
            ship_gbest(network, winner, recipient, best_x, result["best_fitness"])
    population = [best_x, [value + 0.01 for value in best_x], [value - 0.01 for value in best_x]]
    bundle = wan.export_elites(winner, population, [result["best_fitness"], result["best_fitness"] + 0.1, result["best_fitness"] + 0.2])
    for recipient in scores:
        if recipient != winner:
            wan.send(bundle, recipient)
    delivered = {recipient: len(transport.recv(recipient)) for recipient in scores if recipient != winner}
    lattice = build_lattice_stack(
        [
            Machine(f"{cluster}-healthy", health=0.95, capacity=0.8)
            for cluster in scores
        ]
        + [Machine("reuse-lane-0", health=0.55, capacity=0.35)]
        + [Machine("quarantine-0", health=0.1, capacity=0.2, trust=0.2)]
    )
    return {
        "primary_carbon_federate": primary,
        "carbon_rank": rank_clusters_by_carbon(scores, scores),
        "si": result,
        "transport": transport.snapshot(),
        "wan_history": wan.history,
        "vsa_frames_received": {recipient: len(recv_gbest_frames(network, recipient)) for recipient in scores if recipient != winner},
        "packets_delivered": delivered,
        "scratchpad": pad.snapshot(),
        "lattice": lattice,
    }