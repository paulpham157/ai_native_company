from dataclasses import asdict
from pathlib import Path

from artifact_detector import detect_type
from models import Issue, ReviewResult, Evidence
from rules_reviewer import run_rules_review
from schema_reviewer import run_schema_review
from rubric_reviewer import run_rubric_review
from hitl_checker import run_hitl_check


class ReviewOrchestrator:
    def __init__(self):
        self._type_map = None

    def configure_type_map(self, type_map: dict[str, str]):
        base = {"md": "markdown", "markdown": "markdown", "json": "json", "yaml": "yaml", "yml": "yaml"}
        base.update(type_map)
        self._type_map = base

    def review(self, artifact_path: str, mode: str = "quick") -> dict:
        artifact_type = detect_type(artifact_path, self._type_map)

        if not Path(artifact_path).exists():
            return asdict(ReviewResult(
                artifact_path=artifact_path,
                artifact_type=artifact_type,
                issues=[Issue(severity="error", message=f"Artifact not found: {artifact_path}", location="")],
                evidence=[Evidence(source="detector", detail=f"File does not exist: {artifact_path}")],
                confidence_score=0.0,
                need_review=True,
                summary=f"Artifact not found: {artifact_path}",
            ))

        if artifact_type == "unsupported":
            return self._unsupported_result(artifact_path)

        issues = run_rules_review(artifact_path, artifact_type)
        issues += run_schema_review(artifact_path, artifact_type)

        quality_scores = None
        hitl_flags = None
        if mode == "full":
            quality_scores = run_rubric_review(artifact_path, artifact_type)
            hitl_flags = run_hitl_check(artifact_path, artifact_type)

        evidence = [
            Evidence(source=f"{artifact_type}-reviewer", detail=f"Scanned {Path(artifact_path).name}")
        ]

        confidence_score = 0.85 if len(issues) == 0 else 0.7

        return asdict(ReviewResult(
            artifact_path=artifact_path,
            artifact_type=artifact_type,
            issues=issues,
            evidence=evidence,
            confidence_score=confidence_score,
            need_review=False,
            summary=f"Found {len(issues)} issue(s).",
            quality_scores=quality_scores,
            hitl_flags=hitl_flags,
        ))

    def _unsupported_result(self, artifact_path: str) -> dict:
        return asdict(ReviewResult(
            artifact_path=artifact_path,
            artifact_type="unsupported",
            issues=[Issue(severity="warning", message="Unsupported artifact type", location="")],
            evidence=[Evidence(source="detector", detail=f"Cannot review .{Path(artifact_path).suffix.lstrip('.')} files")],
            confidence_score=0.0,
            need_review=True,
            summary=f"Unsupported artifact type: {Path(artifact_path).suffix}",
        ))
