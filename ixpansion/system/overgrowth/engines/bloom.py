def bloom(state: dict, rate: float = 0.1) -> dict:
    state["bloom"] = float(state.get("bloom", 1)) * (1 + rate)
    return state
