#!/usr/bin/env python3

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "script"))

from evidence_tracker import EvidenceTracker
from test_helpers import load_schemas, validate

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


def main():
    global passed, failed
    print("=" * 60)
    print("EVIDENCE TRACKING TEST \u2014 vibe-xthinking-orchestrator")
    print("=" * 60)

    tracker = EvidenceTracker()

    # ── Test 1: Weighted average formula ──
    print("\n[1] Weighted average aggregation")
    chain = [
        {"agent": "Researcher", "claim": "Claim 1", "confidence": 0.80, "source": "Src 1"},
        {"agent": "Explicit Thinker", "claim": "Claim 2", "confidence": 0.70, "source": "Src 2"},
        {"agent": "Value Chain Analyst", "claim": "Claim 3", "confidence": 0.90, "source": "Src 3"},
        {"agent": "Synthesizer", "claim": "Claim 4", "confidence": 0.85, "source": "Src 4"},
        {"agent": "Validator", "claim": "Claim 5", "confidence": 0.75, "source": "Src 5"},
    ]
    # 0.80*0.15 + 0.70*0.20 + 0.90*0.20 + 0.85*0.20 + 0.75*0.25
    # = 0.120 + 0.140 + 0.180 + 0.170 + 0.1875 = 0.7975 → round 0.80
    agg = tracker.aggregate(chain)
    expected = 0.80
    check("aggregate returns weighted average", abs(agg - expected) < 0.01, f"got {agg}, expected {expected}")

    # ── Test 2: Confidence < 0.7 triggers need_review ──
    print("\n[2] Low confidence triggers need_review")
    low_chain = [
        {"agent": "Researcher", "claim": "Weak claim", "confidence": 0.50, "source": "Weak src"},
    ]
    check("aggregate < 0.7 for low confidence", tracker.aggregate(low_chain) < 0.7, f"got {tracker.aggregate(low_chain)}")
    check("needs_review is True for low confidence", tracker.needs_review(low_chain) is True)
    high_chain = [
        {"agent": "Researcher", "claim": "Strong claim", "confidence": 0.95, "source": "Strong src"},
    ]
    check("needs_review is False for high confidence", tracker.needs_review(high_chain) is False)

    # ── Test 3: Empty evidence chain ──
    print("\n[3] Empty evidence chain edge case")
    empty_agg = tracker.aggregate([])
    check("aggregate returns 0.0 for empty chain", empty_agg == 0.0, f"got {empty_agg}")
    check("needs_review is True for empty chain", tracker.needs_review([]) is True)

    # ── Test 4: Schema compliance ──
    print("\n[4] Output validates against evidence-tracking schema")
    schemas = load_schemas()
    evidence_schema = schemas.get("evidence-tracking.schema.json")
    if evidence_schema:
        result = tracker.track(
            evidence_chain=chain,
            analysis_ref="ta-001",
            tracking_id="et-001",
        )
        errs = validate(evidence_schema, result)
        check("track output validates against schema", not errs, "; ".join(e.message for e in errs[:3]))
    else:
        check("evidence-tracking.schema.json exists", False, "schema file not found")

    # ── Test 5: track() returns correct contract fields ──
    print("\n[5] track() output contains all required fields")
    result = tracker.track(
        evidence_chain=chain,
        analysis_ref="ta-001",
        tracking_id="et-001",
    )
    check("has tracking_id", "tracking_id" in result)
    check("has analysis_ref", "analysis_ref" in result)
    check("has evidence_chain", "evidence_chain" in result)
    check("has aggregate_confidence", "aggregate_confidence" in result)
    check("has evidence", "evidence" in result)
    check("has confidence_score", "confidence_score" in result)
    check("has need_review", "need_review" in result)
    check("aggregate_confidence == confidence_score", result["aggregate_confidence"] == result["confidence_score"])
    check("need_review is boolean", isinstance(result["need_review"], bool))

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
