from dataclasses import dataclass, field


@dataclass
class Issue:
    severity: str  # error | warning | info
    message: str
    location: Optional[str] = None


@dataclass
class Evidence:
    source: str
    detail: str


@dataclass
class ReviewResult:
    artifact_path: str
    artifact_type: str  # markdown | json | yaml | unsupported
    evidence: list[Evidence] = field(default_factory=list)
    confidence_score: float = 0.0
    need_review: bool = False
    issues: list[Issue] = field(default_factory=list)
    summary: str = ""
    quality_scores: dict | None = None
    hitl_flags: list | None = None
