"""Guard GitLab pipeline definitions against obvious secret disclosure."""
SECRET_MARKERS = ("SECRET", "TOKEN", "PASSWORD", "PRIVATE_KEY", "ACCESS_KEY")


def validate_pipeline(pipeline_def):
    if not isinstance(pipeline_def, dict):
        return False
    for job_name, job_config in pipeline_def.items():
        if job_name in {"stages", "variables", "workflow", "include", "default"}:
            continue
        if not isinstance(job_config, dict):
            continue
        scripts = job_config.get("script", [])
        if isinstance(scripts, str):
            scripts = [scripts]
        if not isinstance(scripts, list):
            return False
        for script in scripts:
            if not isinstance(script, str):
                return False
            upper = script.upper()
            if any(marker in upper for marker in SECRET_MARKERS):
                return False
    return True


def test_valid_dependency_graph(gitlab_pipelines):
    pipeline = gitlab_pipelines["valid_pipeline"]
    assert validate_pipeline(pipeline) is True
    assert pipeline["test_job"]["dependencies"] == ["build_job"]


def test_unsafe_secret_exposure_blocked(gitlab_pipelines):
    assert validate_pipeline(gitlab_pipelines["unsafe_pipeline"]) is False
