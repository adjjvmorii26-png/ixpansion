def repository_mapping() -> dict[str, list[str]]:
    return {
        "core": ["runtime", "state", "events"],
        "agents": ["observer", "architect", "mutator"],
        "mesh": ["star", "ring", "chaotic"],
    }
