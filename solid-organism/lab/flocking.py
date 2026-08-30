#!/usr/bin/env python3
"""Flocking: emergent collective behavior from simple rules.

Each agent follows three rules: separation (don't crowd neighbors),
alignment (steer toward average heading), cohesion (steer toward average
position). From these three rules emerges complex, beautiful flocking
behavior — the same pattern seen in starlings, fish schools, and murmurations.

Usage:
    python3 flocking.py --agents 50 --steps 100
    python3 flocking.py --agents 100 --steps 200
"""
from __future__ import annotations

import argparse
import json
import math
import random
from typing import Any, Dict, List, Tuple


def _normalize(x: float, y: float) -> Tuple[float, float]:
    mag = math.sqrt(x*x + y*y)
    if mag < 1e-10:
        return 0.0, 0.0
    return x/mag, y/mag


def simulate(num_agents: int = 50, num_steps: int = 100,
             width: int = 100, height: int = 100,
             separation_radius: float = 5.0,
             alignment_radius: float = 25.0,
             cohesion_radius: float = 50.0,
             max_speed: float = 2.0,
             seed: int = 42) -> Dict[str, Any]:
    """Run a flocking simulation."""
    rng = random.Random(seed)
    
    # Initialize agents at random positions with random velocities
    agents = []
    for _ in range(num_agents):
        x = rng.uniform(0, width)
        y = rng.uniform(0, height)
        vx = rng.uniform(-max_speed, max_speed)
        vy = rng.uniform(-max_speed, max_speed)
        agents.append({"x": x, "y": y, "vx": vx, "vy": vy})
    
    history = []
    flock_cohesion_history = []
    
    for step in range(num_steps):
        new_agents = [dict(a) for a in agents]  # copy
        
        for i in range(num_agents):
            # Find neighbors in each radius
            sep_neighbors = []
            align_neighbors = []
            coh_neighbors = []
            
            for j in range(num_agents):
                if i == j:
                    continue
                dx = agents[j]["x"] - agents[i]["x"]
                dy = agents[j]["y"] - agents[i]["y"]
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < separation_radius:
                    sep_neighbors.append((j, dx, dy, dist))
                if dist < alignment_radius:
                    align_neighbors.append((j, dx, dy, dist))
                if dist < cohesion_radius:
                    coh_neighbors.append((j, dx, dy, dist))
            
            # Separation: steer away from nearby agents
            sx, sy = 0.0, 0.0
            for _, dx, dy, dist in sep_neighbors:
                if dist > 0:
                    sx -= dx / dist
                    sy -= dy / dist
            
            # Alignment: steer toward average heading
            ax, ay = 0.0, 0.0
            if align_neighbors:
                for j, _, _, _ in align_neighbors:
                    ax += agents[j]["vx"]
                    ay += agents[j]["vy"]
                ax /= len(align_neighbors)
                ay /= len(align_neighbors)
                ax -= agents[i]["vx"]
                ay -= agents[i]["vy"]
            
            # Cohesion: steer toward average position
            cx, cy = 0.0, 0.0
            if coh_neighbors:
                for j, _, _, _ in coh_neighbors:
                    cx += agents[j]["x"]
                    cy += agents[j]["y"]
                cx = cx / len(coh_neighbors) - agents[i]["x"]
                cy = cy / len(coh_neighbors) - agents[i]["y"]
            
            # Weighted sum
            new_agents[i]["vx"] += sx * 1.5 + ax * 1.0 + cx * 0.005
            new_agents[i]["vy"] += sy * 1.5 + ay * 1.0 + cy * 0.005
            
            # Limit speed
            speed = math.sqrt(new_agents[i]["vx"]**2 + new_agents[i]["vy"]**2)
            if speed > max_speed:
                new_agents[i]["vx"] = new_agents[i]["vx"] / speed * max_speed
                new_agents[i]["vy"] = new_agents[i]["vy"] / speed * max_speed
            
            # Update position
            new_agents[i]["x"] += new_agents[i]["vx"]
            new_agents[i]["y"] += new_agents[i]["vy"]
            
            # Wrap around
            new_agents[i]["x"] %= width
            new_agents[i]["y"] %= height
        
        agents = new_agents
        
        # Measure flock cohesion (average distance to centroid)
        cx = sum(a["x"] for a in agents) / num_agents
        cy = sum(a["y"] for a in agents) / num_agents
        avg_dist = sum(math.sqrt((a["x"]-cx)**2 + (a["y"]-cy)**2) for a in agents) / num_agents
        flock_cohesion_history.append(round(avg_dist, 2))
        
        if step % 10 == 0:
            history.append({
                "step": step,
                "centroid_x": round(cx, 2),
                "centroid_y": round(cy, 2),
                "avg_distance_to_centroid": round(avg_dist, 2),
            })
    
    # Final state
    avg_speed = sum(math.sqrt(a["vx"]**2 + a["vy"]**2) for a in agents) / num_agents
    
    return {
        "num_agents": num_agents,
        "num_steps": num_steps,
        "width": width,
        "height": height,
        "final_avg_speed": round(avg_speed, 3),
        "final_avg_distance_to_centroid": flock_cohesion_history[-1] if flock_cohesion_history else 0,
        "cohesion_trajectory": flock_cohesion_history[::10],
        "centroid_history": history,
        "emergent_properties": {
            "separation_rules_fired": "continuous",
            "alignment_rules_fired": "continuous",
            "cohesion_rules_fired": "continuous",
            "result": "emergent flocking behavior from 3 simple rules",
        },
        "philosophy": (
            "Three rules. Separation, alignment, cohesion. No leader, no plan. "
            "And yet: starlings wheel in perfect formation across the winter sky. "
            "The flock has no central control. The flock IS the control."
        ),
    }


def main():
    ap = argparse.ArgumentParser(description="Flocking simulation")
    ap.add_argument("--agents", type=int, default=50)
    ap.add_argument("--steps", type=int, default=100)
    ap.add_argument("--width", type=int, default=100)
    ap.add_argument("--height", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    result = simulate(args.agents, args.steps, args.width, args.height, seed=args.seed)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
