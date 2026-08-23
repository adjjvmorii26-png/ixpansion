def branch_region(branch: str) -> str:
    safe = "".join(char if char.isalnum() else "-" for char in branch.lower())
    return f"branch-{safe}"
