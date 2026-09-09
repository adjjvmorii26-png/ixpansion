"""
resonance_field — Models the organism's resonance as a living field.
Modules emit resonance waves that interact, interfere, and create patterns.
The field visualizes the organism's collective harmonic state.
"""
import json
import time
import math
import hashlib
from typing import Dict, List, Tuple

class ResonanceField:
    def __init__(self, width: int = 50, height: int = 50):
        self.width = width
        self.height = height
        self.field = [[0.0 for _ in range(width)] for _ in range(height)]
        self.sources = []
        self.time = 0
        self.history = []
    
    def add_source(self, x: int, y: int, frequency: float, amplitude: float, 
                   phase: float = 0, name: str = "") -> Dict:
        source = {
            "x": x % self.width,
            "y": y % self.height,
            "frequency": frequency,
            "amplitude": amplitude,
            "phase": phase,
            "name": name or f"source_{len(self.sources)}",
            "id": hashlib.sha256(f"{x}{y}{time.time()}".encode()).hexdigest()[:6]
        }
        self.sources.append(source)
        return source
    
    def step(self):
        """Advance the field by one time step."""
        self.time += 0.1
        
        for y in range(self.height):
            for x in range(self.width):
                value = 0
                for src in self.sources:
                    dx = x - src["x"]
                    dy = y - src["y"]
                    dist = math.sqrt(dx*dx + dy*dy) + 1
                    
                    # Wave equation: A * sin(k*r - ω*t + φ) / r
                    wave = (src["amplitude"] * 
                           math.sin(src["frequency"] * dist * 0.1 - 
                                    src["frequency"] * self.time + src["phase"]) /
                           (1 + dist * 0.1))
                    value += wave
                
                self.field[y][x] = value
        
        # Record statistics
        flat = [self.field[y][x] for y in range(self.height) for x in range(self.width)]
        mean_val = sum(flat) / len(flat)
        max_val = max(flat)
        min_val = min(flat)
        
        self.history.append({
            "time": self.time,
            "mean": round(mean_val, 4),
            "max": round(max_val, 4),
            "min": round(min_val, 4),
            "energy": round(sum(v*v for v in flat) / len(flat), 4)
        })
        
        if len(self.history) > 100:
            self.history.pop(0)
    
    def get_field_stats(self) -> Dict:
        flat = [self.field[y][x] for y in range(self.height) for x in range(self.width)]
        return {
            "sources": len(self.sources),
            "field_size": f"{self.width}x{self.height}",
            "time": round(self.time, 2),
            "mean": round(sum(flat) / len(flat), 4),
            "max": round(max(flat), 4),
            "min": round(min(flat), 4),
            "energy": round(sum(v*v for v in flat) / len(flat), 4),
            "constructive_points": sum(1 for v in flat if v > 0.5),
            "destructive_points": sum(1 for v in flat if v < -0.5)
        }
    
    def find_interference_patterns(self) -> List[Dict]:
        """Find constructive and destructive interference points."""
        patterns = []
        for y in range(self.height):
            for x in range(self.width):
                val = self.field[y][x]
                if abs(val) > 0.3:
                    pattern_type = "constructive" if val > 0 else "destructive"
                    patterns.append({
                        "x": x, "y": y,
                        "type": pattern_type,
                        "intensity": round(abs(val), 4)
                    })
        
        # Cluster nearby points
        clusters = []
        visited = set()
        for p in sorted(patterns, key=lambda p: p["intensity"], reverse=True):
            key = (p["x"], p["y"])
            if key not in visited:
                cluster = [p]
                visited.add(key)
                for q in patterns:
                    qkey = (q["x"], q["y"])
                    if qkey not in visited and abs(q["x"]-p["x"]) <= 2 and abs(q["y"]-p["y"]) <= 2:
                        cluster.append(q)
                        visited.add(qkey)
                if len(cluster) >= 2:
                    avg_intensity = sum(c["intensity"] for c in cluster) / len(cluster)
                    clusters.append({
                        "center": (p["x"], p["y"]),
                        "type": p["type"],
                        "size": len(cluster),
                        "avg_intensity": round(avg_intensity, 4)
                    })
        
        return sorted(clusters, key=lambda c: c["avg_intensity"], reverse=True)[:5]
    
    def render_ascii(self) -> str:
        """Render the field as ASCII art."""
        chars = " ·∘●◎◉★"
        lines = []
        for y in range(0, self.height, 3):
            line = ""
            for x in range(0, self.width, 2):
                val = self.field[y][x]
                idx = int((val + 1) / 2 * (len(chars) - 1))
                idx = max(0, min(len(chars) - 1, idx))
                line += chars[idx]
            lines.append(line)
        return "\n".join(lines)


if __name__ == "__main__":
    field = ResonanceField(40, 30)
    
    print("═══════════════════════════════════════")
    print("   RESONANCE FIELD — Living Wave Pattern")
    print("═══════════════════════════════════════\n")
    
    # Add sources
    field.add_source(10, 15, frequency=1.0, amplitude=1.0, name="coherence_core")
    field.add_source(30, 10, frequency=0.8, amplitude=0.7, name="entropy_field")
    field.add_source(20, 25, frequency=1.2, amplitude=0.5, name="dream_weaver")
    field.add_source(35, 20, frequency=0.6, amplitude=0.8, name="resonance_nexus")
    
    print("Sources:")
    for s in field.sources:
        print(f"  ◎ {s['name']} at ({s['x']},{s['y']}) freq={s['frequency']} amp={s['amplitude']}")
    
    print("\nSimulating 20 steps...")
    for i in range(20):
        field.step()
    
    stats = field.get_field_stats()
    print(f"\nField: {stats['field_size']}, time={stats['time']}")
    print(f"Mean: {stats['mean']}, Max: {stats['max']}, Min: {stats['min']}")
    print(f"Energy: {stats['energy']}")
    print(f"Constructive points: {stats['constructive_points']}")
    print(f"Destructive points: {stats['destructive_points']}")
    
    patterns = field.find_interference_patterns()
    print(f"\nTop interference patterns:")
    for p in patterns:
        print(f"  {p['type']} at {p['center']} — intensity={p['avg_intensity']}, size={p['size']}")
    
    print(f"\nField visualization:")
    print(field.render_ascii())
