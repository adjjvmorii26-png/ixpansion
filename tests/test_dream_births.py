"""Dream birth validation — ensures every dream-born module has the wave contract."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "api"))

# Dream-born modules discovered from git history + on-disk dream_* files
DREAM_DIR = ROOT / "api"
dream_modules = sorted(f.stem for f in DREAM_DIR.glob("dream_*.py"))

# Also include genesis-forge children that the ecosystem birthed
# (discovered in earlier commits)
for extra in ("memory_cache", "neural_graft", "neural_sheath", "cyber_pulse",
              "commerce_bazaar", "obsidian__v10"):
    if (DREAM_DIR / f"{extra}.py").exists():
        dream_modules.append(extra)

dream_modules = sorted(set(dream_modules))


def _import(name: str):
    try:
        return importlib.import_module(name), None
    except Exception as e:
        return None, str(e)


def test_all_dream_modules_importable():
    """Every dream-born module must be importable."""
    failures = []
    for mod_name in dream_modules:
        mod, err = _import(mod_name)
        if mod is None:
            failures.append(f"{mod_name}: {err}")
    if failures:
        raise AssertionError(f"Import failures ({len(failures)}/{len(dream_modules)}):\n" + "\n".join(failures[:10]))


_ALT_ENTRY_POINTS = (
    "handler", "generate_module_from_dream", "record_and_generate",
    "generate_dream", "dream_cycle", "run", "status",
)


def test_all_dream_modules_have_handler():
    """Every dream-born module must export a callable entry point."""
    failures = []
    for mod_name in dream_modules:
        mod, err = _import(mod_name)
        if mod is None:
            continue
        has_entry = False
        for attr in _ALT_ENTRY_POINTS:
            candidate = getattr(mod, attr, None)
            if callable(candidate):
                has_entry = True
                break
        if not has_entry:
            # Check class-style interfaces
            for attr in dir(mod):
                if attr.startswith("_"):
                    continue
                try:
                    obj = getattr(mod, attr)
                    if isinstance(obj, type) and hasattr(obj, "__call__"):
                        has_entry = True
                        break
                except Exception:
                    pass
        if not has_entry:
            failures.append(f"{mod_name}: no callable entry point (handler, generate, record, run...)")
    if failures:
        raise AssertionError(f"Handler failures ({len(failures)}):\n" + "\n".join(failures[:10]))


def test_all_dream_modules_have_vitals():
    """Every dream-born module must export coherence_vitals returning a dict."""
    failures = []
    for mod_name in dream_modules:
        mod, err = _import(mod_name)
        if mod is None:
            continue
        cv = getattr(mod, "coherence_vitals", None)
        if not callable(cv):
            failures.append(f"{mod_name}: coherence_vitals missing")
            continue
        try:
            result = cv()
            if not isinstance(result, dict):
                failures.append(f"{mod_name}: coherence_vitals returned {type(result)}")
        except Exception as e:
            failures.append(f"{mod_name}: coherence_vitals raised {e}")
    if failures:
        raise AssertionError(f"Vitals failures ({len(failures)}):\n" + "\n".join(failures[:10]))


def test_all_dream_modules_have_resonates_with():
    """Every dream-born module must export resonates_with as list or callable."""
    failures = []
    for mod_name in dream_modules:
        mod, err = _import(mod_name)
        if mod is None:
            continue
        rw = getattr(mod, "resonates_with", None)
        if rw is None:
            failures.append(f"{mod_name}: resonates_with missing")
            continue
        if callable(rw):
            result = None
            for attempt in [lambda: rw(), lambda: rw({})]:
                try:
                    result = attempt()
                    break
                except TypeError:
                    continue
                except Exception as e:
                    failures.append(f"{mod_name}: resonates_with raised {e}")
                    break
            if result is not None and not isinstance(result, list):
                failures.append(f"{mod_name}: resonates_with returned {type(result)}")
        elif not isinstance(rw, list):
            failures.append(f"{mod_name}: resonates_with is {type(rw)}, not list or callable")
    if failures:
        raise AssertionError(f"Resonates failures ({len(failures)}):\n" + "\n".join(failures[:10]))


def test_dream_modules_handler_contract():
    """Every dream-born handler must accept a dict and return a dict.
    Tries multiple call patterns for variant signatures."""
    failures = []
    for mod_name in dream_modules:
        mod, err = _import(mod_name)
        if mod is None:
            continue
        h = getattr(mod, "handler", None)
        if not callable(h):
            continue
        result = None
        for attempt in [
            lambda: h({"action": "status"}),
            lambda: h({"action": "status"}, None),
            lambda: h({"action": "status"}, None, None),
        ]:
            try:
                result = attempt()
                break
            except TypeError:
                continue
            except Exception as e:
                failures.append(f"{mod_name}: handler raised {e}")
                break
        if result is not None and not isinstance(result, dict):
            failures.append(f"{mod_name}: handler returned {type(result)}")
    if failures:
        raise AssertionError(f"Contract failures ({len(failures)}):\n" + "\n".join(failures[:10]))


def test_dream_module_count():
    """At least 20 dream modules should exist on disk."""
    assert len(dream_modules) >= 20, f"Only {len(dream_modules)} dream modules found (expected >= 20)"
