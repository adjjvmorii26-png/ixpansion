"""Paradox Resonator - Detects contradictory patterns in code."""
from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ParadoxResonator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.paradoxes = []
        self.modules = []

    def scan_module(self, name: str, filepath: Path):
        text = filepath.read_text(errors='replace')
        lines = text.splitlines()
        funcs = [ln.strip().split('(')[0].replace('def ', '') for ln in lines if ln.strip().startswith('def ')]
        classes = [ln.strip().split('class ')[1].split('(')[0] for ln in lines if ln.strip().startswith('class ')]
        self.modules.append({
            'name': name, 'functions': funcs, 'classes': classes,
            'lines': len(lines), 'size': filepath.stat().st_size,
        })

    def detect_paradoxes(self):
        for mod in self.modules:
            creates = [f for f in mod['functions'] if 'create' in f or 'build' in f or 'add' in f]
            destroys = [f for f in mod['functions'] if 'destroy' in f or 'remove' in f or 'delete' in f]
            if creates and destroys:
                self.paradoxes.append({
                    'type': 'creation_destruction',
                    'module': mod['name'],
                    'detail': f'Has both creation ({creates[0]}) and destruction ({destroys[0]})',
                    'creative_tension': 'high',
                })
            if mod['lines'] > 200 and len(mod['classes']) == 0:
                self.paradoxes.append({
                    'type': 'massive_procedural',
                    'module': mod['name'],
                    'detail': f"{mod['lines']} lines but no classes",
                    'creative_tension': 'medium',
                })

    def report(self):
        self.detect_paradoxes()
        tensions = {}
        for p in self.paradoxes:
            t = p['creative_tension']
            tensions[t] = tensions.get(t, 0) + 1
        return {
            'resonator': 'paradox_resonator',
            'module_count': len(self.modules),
            'paradox_count': len(self.paradoxes),
            'tension_distribution': tensions,
            'paradoxes': self.paradoxes[:15],
        }


def demo():
    resonator = ParadoxResonator(seed=42)
    for base in [ROOT / 'api', ROOT / 'lab' / 'experiments', ROOT / 'bridges']:
        if base.exists():
            for py in base.glob('*.py'):
                if py.name.startswith('_') or py.name.startswith('test_'):
                    continue
                resonator.scan_module(py.stem, py)
    return resonator.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == '__main__':
    main()
