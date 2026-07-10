import re
from pathlib import Path


_CRITICAL_PATTERNS = [
    {
        "item_id": "critical-deadline",
        "question": "Is the deadline realistic given current resources?",
        "rationale": "AI cannot assess resource availability or team capacity",
        "pattern": r"(?i)\bdeadline\b.*\d{4}[-/]\d{1,2}[-/]\d{1,2}",
    },
    {
        "item_id": "critical-budget",
        "question": "Is the budget allocation accurate and approved?",
        "rationale": "Budget figures require human approval and context",
        "pattern": r"(?i)\$\s*\d[\d,]*",
    },
    {
        "item_id": "critical-sla",
        "question": "Are the SLA targets aligned with service capacity?",
        "rationale": "SLAs require stakeholder agreement",
        "pattern": r"(?i)\bSLA\b",
    },
]


def run_hitl_check(artifact_path: str, artifact_type: str) -> list | None:
    if artifact_type not in ("markdown", "json", "yaml"):
        return None
    content = Path(artifact_path).read_text(encoding="utf-8")
    flags = []
    for rule in _CRITICAL_PATTERNS:
        if re.search(rule["pattern"], content):
            flags.append({
                "item_id": rule["item_id"],
                "question": rule["question"],
                "rationale": rule["rationale"],
            })
    return flags
