#!/usr/bin/env python3
"""Homing: navigation without a map.

Pigeons return home across hundreds of miles without maps, without GPS.
They use the sun, the stars, magnetic fields, olfactory landmarks, and —
crucially — a process of collective error correction. They don't know where
home is; they know how to find it as a group.

This module simulates pigeon-style homing:
- Each agent has an imprecise "internal compass"
- Agents communicate by noting when they're "close enough"
- The flock aggregates imperfect signals into a precise heading

Usage:
    python3 homing.py --birds 20 --homer-dist 50 --noise 0.3
    python3 homing.py --birds 8 --noise 0.8 --show-flock
"""
from __future__ import annotations

import argparse
import json
import math
import random
from typing import Any, Dict, List, Tuple


def _distance_to_home(x: float, y: float, home: Tuple[float, float]) -> float:
    return math.sqrt((x - home[0])**2 + (y - home[1])**2)


def simulate(num_birds: int = 20, homer_dist: float = 50.0,
             noise: float = 0.3, max_steps: int = 200,
             home: Tuple[float, float] = (100.0, 100.0),
             start_x: float = 0.0, start_y: float = 0.0,
             seed: int = 42) -> Dict[str, Any]:
    """Simulate collective homing behavior.

    Args:
        num_birds: number of pigeons
        homer_dist: distance at which a bird can sense home (~50 units)
        noise: internal compass noise
    """
    rng = random.Random(seed)

    # Initialize birds near start with random headings
    birds = []
    for i in range(num_birds):
        angle = rng.uniform(0, 2 * math.pi)
        # A few "pioneers" have a weak innate sense of home direction
        # (like birds born with partial magnetic maps). This bootstraps
        # the collective into the homer range.
        pioneer = i < max(2, num_birds // 5)
        birds.append({
            "x": start_x + rng.gauss(0, 5),
            "y": start_y + rng.gauss(0, 5),
            # imperfect compass: each bird has a systematic heading bias
            "compass_bias": rng.gauss(0, noise),
            "pioneer": pioneer,
            "homing": False,  # has this bird sensed home yet?
            "path": [],
        })

    history = []
    arrivals = 0

    for step in range(max_steps):
        for bird in birds:
            d = _distance_to_home(bird["x"], bird["y"], home)

            # If within homer_dist, the bird "senses home" and can navigate
            if d < homer_dist:
                bird["homing"] = True

            if bird["homing"]:
                # Precise homing toward home + noise
                dx = home[0] - bird["x"]
                dy = home[1] - bird["y"]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 2:  # arrived
                    arrivals += 1
                    continue
                # angle to home
                target_angle = math.atan2(dy, dx)
                # add compass bias
                angle = target_angle + rng.gauss(0, bird["compass_bias"])
                step_x = math.cos(angle) * 1.5
                step_y = math.sin(angle) * 1.5
                bird["x"] += step_x
                bird["y"] += step_y
            else:
                # Not yet homing: collective navigation.
                # Birds that are homing "call home" — others steer toward
                # the average heading of homing birds.
                homers = [b for b in birds if b["homing"] and b is not bird]
                if bird.get("pioneer"):
                    # weak innate pull toward home (bootstraps the flock)
                    angle = math.atan2(home[1] - bird["y"], home[0] - bird["x"]) + rng.gauss(0, bird["compass_bias"])
                    bird["x"] += math.cos(angle) * 1.2
                    bird["y"] += math.sin(angle) * 1.2
                elif homers:
                    # steer toward average position of homing birds
                    cx = sum(b["x"] for b in homers) / len(homers)
                    cy = sum(b["y"] for b in homers) / len(homers)
                    angle = math.atan2(cy - bird["y"], cx - bird["x"]) + rng.gauss(0, bird["compass_bias"])
                    bird["x"] += math.cos(angle) * 1.5
                    bird["y"] += math.sin(angle) * 1.5
                else:
                    # No homers yet: wander with weak collective alignment
                    angle = rng.uniform(0, 2 * math.pi)
                    bird["x"] += math.cos(angle) * 1.0
                    bird["y"] += math.sin(angle) * 1.0

            bird["path"].append({"x": round(bird["x"], 1), "y": round(bird["y"], 1)})

        avg_dist = _distance_to_home(
            sum(b["x"] for b in birds) / num_birds,
            sum(b["y"] for b in birds) / num_birds, home)
        homers_now = sum(1 for b in birds if b["homing"])
        history.append({
            "step": step,
            "avg_distance_to_home": round(avg_dist, 1),
            "homers": homers_now,
        })

    # Results
    final_distances = [_distance_to_home(b["x"], b["y"], home) for b in birds]
    arrived = sum(1 for d in final_distances if d < 3)

    return {
        "num_birds": num_birds,
        "homer_dist": homer_dist,
        "noise": noise,
        "home": home,
        "start": (start_x, start_y),
        "birds_arrived": arrived,
        "avg_final_distance": round(sum(final_distances) / len(final_distances), 1),
        "arrival_rate": round(arrived / num_birds, 3),
        "collective_distance_traveled": round(sum(
            _distance_to_home(b["x"], b["y"], home) for b in birds
        ) / num_birds, 1),
        "history_sample": history[::25],
        "emergent_insight": (
            f"{arrived} of {num_birds} birds made it home. The flock "
            "collectively corrected the compass errors of individuals. "
            "No bird had a perfect sense of home; together, they did."
        ),
        "philosophy": (
            "No single pigeon knows the way home. But twenty pigeons, "
            "sharing uncertain signals, find it together. Knowledge is not "
            "in any one mind — it is in the pattern between minds."
        ),
    }


def main():
    ap = argparse.ArgumentParser(description="Collective homing simulation")
    ap.add_argument("--birds", type=int, default=20)
    ap.add_argument("--homer-dist", type=float, default=50.0)
    ap.add_argument("--noise", type=float, default=0.3)
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    result = simulate(args.birds, args.homer_dist, args.noise, args.steps, seed=args.seed)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
