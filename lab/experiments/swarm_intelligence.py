from __future__ import annotations
import random

class SwarmAgent:
    def __init__(self, x, y, seed=42):
        self.x, self.y = x, y
        self.vx = self.vy = 0.0
        self.rng = random.Random(seed)
    def update(self, neighbors, food):
        sx = sy = 0.0
        for n in neighbors:
            dx, dy = self.x-n.x, self.y-n.y
            d = (dx*dx+dy*dy)**0.5+0.01
            if d < 2.0: sx += dx/d; sy += dy/d
        self.vx += sx*0.05; self.vy += sy*0.05
        if food:
            c = min(food, key=lambda f:(f[0]-self.x)**2+(f[1]-self.y)**2)
            dx, dy = c[0]-self.x, c[1]-self.y
            d = (dx*dx+dy*dy)**0.5+0.01
            self.vx += dx/d*0.02; self.vy += dy/d*0.02
        self.vx += self.rng.uniform(-0.01,0.01)
        self.vy += self.rng.uniform(-0.01,0.01)
        sp = (self.vx**2+self.vy**2)**0.5
        if sp > 0.5: self.vx=self.vx/sp*0.5; self.vy=self.vy/sp*0.5
        self.x += self.vx; self.y += self.vy

class SwarmSimulation:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.agents = []; self.food = []; self.epoch = 0
    def populate(self, count=20):
        for i in range(count):
            self.agents.append(SwarmAgent(self.rng.uniform(-5,5), self.rng.uniform(-5,5), i))
        for _ in range(5):
            self.food.append((self.rng.uniform(-5,5), self.rng.uniform(-5,5)))
    def tick(self):
        self.epoch += 1
        for a in self.agents:
            a.update([x for x in self.agents if x is not a], self.food)
        eaten = [f for f in self.food if any((a.x-f[0])**2+(a.y-f[1])**2<0.5 for a in self.agents)]
        for e in eaten:
            if e in self.food: self.food.remove(e)
    def report(self):
        ps = [(a.x,a.y) for a in self.agents]
        ax = sum(p[0] for p in ps)/max(1,len(ps))
        ay = sum(p[1] for p in ps)/max(1,len(ps))
        sp = (sum((p[0]-ax)**2+(p[1]-ay)**2 for p in ps)/max(1,len(ps)))**0.5
        return {"swarm":"swarm_intelligence","epoch":self.epoch,"agents":len(self.agents), "food":len(self.food),"center":(round(ax,2),round(ay,2)),"spread":round(sp,2)}
                

def demo():
    s = SwarmSimulation(42); s.populate(20)
    for _ in range(30): s.tick()
    return s.report()
def main():
    import json; print(json.dumps(demo(),indent=2))
if __name__=='__main__': main()
