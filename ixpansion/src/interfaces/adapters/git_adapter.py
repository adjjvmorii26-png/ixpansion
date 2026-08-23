import subprocess


def current_branch(cwd: str | None = None) -> str:
    result = subprocess.run(["git", "branch", "--show-current"], cwd=cwd, check=True, text=True, capture_output=True)
    return result.stdout.strip()
