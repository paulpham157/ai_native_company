import json
from pathlib import Path

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False


def run_schema_review(artifact_path: str, artifact_type: str) -> list:
    issues = []
    if artifact_type == "json":
        try:
            json.loads(Path(artifact_path).read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            issues.append({
                "severity": "error",
                "message": f"JSON parse error: {e.msg}",
                "location": f"line {e.lineno}",
            })
    elif artifact_type == "yaml" and HAVE_YAML:
        try:
            yaml.safe_load(Path(artifact_path).read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            issues.append({
                "severity": "error",
                "message": f"YAML parse error: {e}",
                "location": "",
            })
    return issues
