def should_grow(changed_paths: list[str]) -> bool:
    return any(path.startswith(("ixpansion/src/", "ixpansion/engine/")) for path in changed_paths)
