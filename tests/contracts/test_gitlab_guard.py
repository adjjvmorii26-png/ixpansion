"""Guard GitLab pipeline structure and obvious secret disclosure."""
import re

SECRET_REFERENCE = re.compile(
    r"\$(?:\{)?[A-Z0-9_]*(?:SECRET|TOKEN|PASSWORD|PRIVATE_KEY|ACCESS_KEY)[A-Z0-9_]*(?:\})?",
    re.IGNORECASE,
)
OUTPUT_COMMAND = re.compile(r"\b(?:echo|printf|printenv)\b", re.IGNORECASE)


def validate_pipeline(pipeline_def):
    if not isinstance(pipeline_def, dict):
        return False
    stages = pipeline_def.get("stages", [])
    if not isinstance(stages, list) or not all(isinstance(stage, str) for stage in stages):
        return False

    jobs = {
        name: config
        for name, config in pipeline_def.items()
        if name not in {"stages", "variables", "workflow", "include", "default"}
        and isinstance(config, dict)
    }
    for name, job in jobs.items():
        stage = job.get("stage", "test")
        if stage not in stages:
            return False
        dependencies = job.get("dependencies", [])
        if not isinstance(dependencies, list):
            return False
        for dependency in dependencies:
            if dependency not in jobs:
                return False
            dependency_stage = jobs[dependency].get("stage", "test")
            if stages.index(dependency_stage) >= stages.index(stage):
                return False

        scripts = job.get("script", [])
        if isinstance(scripts, str):
            scripts = [scripts]
        if not isinstance(scripts, list):
            return False
        for script in scripts:
            if not isinstance(script, str):
                return False
            if OUTPUT_COMMAND.search(script) and SECRET_REFERENCE.search(script):
                return False
            if re.search(r"(^|\s)set\s+-[a-zA-Z]*x", script):
                return False
    return True


def test_valid_dependency_graph(gitlab_pipelines):
    pipeline = gitlab_pipelines["valid_pipeline"]
    assert validate_pipeline(pipeline) is True
    assert pipeline["test_job"]["dependencies"] == ["build_job"]


def test_unsafe_secret_exposure_blocked(gitlab_pipelines):
    assert validate_pipeline(gitlab_pipelines["unsafe_pipeline"]) is False


def test_unknown_dependency_blocked(gitlab_pipelines):
    pipeline = {
        "stages": ["build", "test"],
        "test_job": {"stage": "test", "dependencies": ["missing_job"], "script": ["pytest"]},
    }
    assert validate_pipeline(pipeline) is False
