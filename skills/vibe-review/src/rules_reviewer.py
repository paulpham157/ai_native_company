from pathlib import Path


def run_rules_review(artifact_path: str, artifact_type: str) -> list:
    if artifact_type != "markdown":
        return []
    content = Path(artifact_path).read_text(encoding="utf-8")
    issues = []
    has_h1 = any(line.strip().startswith("# ") for line in content.splitlines())
    if not has_h1:
        issues.append({
            "severity": "warning",
            "message": "Document should have a title (h1)",
            "location": "line 1",
        })
    return issues
