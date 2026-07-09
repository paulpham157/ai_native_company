#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "script"))

from evidence_validator import EvidenceValidator
from agent_runner import FakeAgentRunner
from orchestrator import XThinkingOrchestrator

passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  \u2713 {name}")
    else:
        failed += 1
        print(f"  \u2717 {name} \u2014 {detail}")


def make_handoff():
    return {
        "request_id": "req-001",
        "analysis_type": "topic",
        "context": {
            "charter_summary": "Test charter",
            "okr_summary": "Test OKRs",
            "industry_context": "Test industry",
        },
        "evidence": [],
        "confidence_score": 0.8,
        "need_review": False,
    }


def main():
    global passed, failed
    print("=" * 60)
    print("EVIDENCE VALIDATOR TEST \u2014 vibe-xthinking-orchestrator")
    print("=" * 60)

    validator = EvidenceValidator()

    # ── Test 1: Source verification ──
    print("\n[1] Source verification")
    clean = [
        {"agent": "Researcher", "claim": "Market growing", "confidence": 0.9, "source": "IDC 2025"},
        {"agent": "Validator", "claim": "Analysis sound", "confidence": 0.85, "source": "Cross-check"},
    ]
    result = validator.assess(clean)
    check("valid evidence has no gaps", len(result.get("gaps", [])) == 0)

    missing_source = [
        {"agent": "Researcher", "claim": "Market growing", "confidence": 0.9, "source": ""},
    ]
    result = validator.assess(missing_source)
    check("missing source detected as gap", len(result.get("gaps", [])) > 0)
    check("gap describes missing source issue",
          any("source" in g.get("issue", "").lower() for g in result["gaps"]))

    # ── Test 2: Confidence bounds ──
    print("\n[2] Confidence bounds")
    out_of_range = [
        {"agent": "Researcher", "claim": "Claim 1", "confidence": 1.5, "source": "Src"},
        {"agent": "Researcher", "claim": "Claim 2", "confidence": -0.1, "source": "Src"},
    ]
    result = validator.assess(out_of_range)
    check("out-of-range confidence flagged as issue",
          len(result.get("issues", [])) > 0 or len(result.get("gaps", [])) > 0)

    # ── Test 3: Empty evidence chain ──
    print("\n[3] Empty evidence chain")
    result = validator.assess([])
    check("total_evidence is 0", result.get("total_evidence") == 0)
    check("no errors for empty chain", len(result.get("gaps", [])) == 0)

    # ── Test 4: Duplicate claim detection ──
    print("\n[4] Duplicate claim detection")
    duplicates = [
        {"agent": "Researcher", "claim": "Market growing 35%", "confidence": 0.9, "source": "IDC"},
        {"agent": "Explicit Thinker", "claim": "Market growing 35%", "confidence": 0.7, "source": "Gartner"},
    ]
    result = validator.assess(duplicates)
    check("duplicate claims detected", len(result.get("conflicts", [])) > 0 or len(result.get("issues", [])) > 0)

    # ── Test 5: Assessment summary ──
    print("\n[5] Assessment summary")
    result = validator.assess(clean)
    check("result has assessment string", "assessment" in result)
    check("assessment is non-empty", len(result.get("assessment", "")) > 0)
    check("total_evidence matches", result.get("total_evidence") == len(clean))
    check("valid_count matches", result.get("valid_count") == len(clean))

    # ── Test 6: EvidenceValidator is Checkpoint-aware? No — but orchestrator integration ──
    print("\n[6] Orchestrator integration — validator output in artifact")
    outputs = {
        "research:Researcher": {
            "findings": "research done",
            "evidence": [
                {"claim": "Market growing", "confidence": 0.9, "source": "IDC 2025"},
            ],
        },
        "thinking:Explicit Thinker": {
            "assumptions": [], "evidence": [],
        },
        "thinking:Value Chain Analyst": {
            "analysis": "done", "evidence": [],
        },
        "synthesis:Synthesizer": {
            "key_insight": "synthesis done", "evidence": [],
        },
        "validation:Validator": {
            "result": "validated",
            "evidence": [
                {"claim": "Validation complete", "confidence": 0.85, "source": "Cross-check"},
            ],
        },
    }
    orch = XThinkingOrchestrator(
        mode="topic",
        agent_runner=FakeAgentRunner(outputs),
        evidence_validator=validator,
        checkpoint=None,
    )
    result = orch.execute(make_handoff())
    check("artifact has validation key", "validation" in result)
    check("validation is dict", isinstance(result.get("validation"), dict))
    check("artifact produced successfully", "analysis_id" in result)

    # ── Test 7: Validation summary appears in artifact ──
    print("\n[7] Validation summary in final output")
    mixed = [
        {"agent": "Researcher", "claim": "Good claim", "confidence": 0.9, "source": "Valid source"},
        {"agent": "Explicit Thinker", "claim": "No source claim", "confidence": 0.5, "source": ""},
    ]
    result = validator.assess(mixed)
    check("gaps list present", "gaps" in result)
    gap_count = len(result["gaps"])
    check(f"detected {gap_count} gap(s)", gap_count == 1, f"expected 1, got {gap_count}")
    check("valid_count reflects gaps", result["valid_count"] == result["total_evidence"] - gap_count)

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
