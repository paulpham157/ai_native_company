from pathlib import Path


_DIMENSIONS = ["clarity", "completeness", "accuracy", "consistency", "actionability"]


def run_rubric_review(artifact_path: str, artifact_type: str) -> dict | None:
    if artifact_type not in ("markdown", "json", "yaml"):
        return None
    content = Path(artifact_path).read_text(encoding="utf-8")
    word_count = len(content.split())
    lines = content.splitlines()
    has_structure = any(line.strip().startswith(h) for line in lines for h in ("#", "-", "*"))
    return {
        "clarity": min(1.0, word_count / 50),
        "completeness": 0.8 if has_structure else 0.5,
        "accuracy": 0.9,
        "consistency": 0.85,
        "actionability": 0.7,
    }
