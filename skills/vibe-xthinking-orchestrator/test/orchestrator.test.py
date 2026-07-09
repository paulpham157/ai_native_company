#!/usr/bin/env python3

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "script"))

from agent_runner import AgentRunner, FakeAgentRunner
from orchestrator import XThinkingOrchestrator
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


def make_handoff_brief(**overrides):
    return {
        "request_id": "req-001",
        "analysis_type": "topic",
        "context": {
            "charter_summary": "Digital transformation charter",
            "okr_summary": "OKR: 30% revenue from digital channels",
            "industry_context": "FinTech industry in Southeast Asia",
        },
        "key_questions": ["What cloud strategy?", "What regulatory concerns?"],
        "evidence": [
            {"claim": "FinTech market growing", "source": "Industry report 2025"},
        ],
        "confidence_score": 0.85,
        "need_review": False,
        **overrides,
    }


def make_fake_outputs():
    return {
        "research:Researcher": {
            "findings": {
                "market_trends": "Cloud adoption growing 35% YoY",
                "regulatory": "Data residency required by MAS",
            },
            "evidence": [
                {"claim": "Cloud adoption in FinTech growing 35% YoY", "confidence": 0.9, "source": "IDC Financial Insights 2025"},
                {"claim": "MAS requires data residency", "confidence": 0.85, "source": "MAS TRM 2024"},
            ],
        },
        "thinking:Explicit Thinker": {
            "assumptions": ["Cloud infra more secure than on-prem"],
            "logic_chain": ["Adoption growing → more vendors → better security"],
            "gaps": ["Zero trust architecture depth unknown"],
            "evidence": [
                {"claim": "Security assumptions valid for major providers", "confidence": 0.75, "source": "AWS Security Whitepaper"},
            ],
        },
        "thinking:Value Chain Analyst": {
            "value_chain_analysis": "Cloud enables faster time-to-market for new features",
            "evidence": [
                {"claim": "Cloud enables faster time-to-market", "confidence": 0.85, "source": "Porter value chain analysis"},
                {"claim": "Phased migration reduces operational risk", "confidence": 0.82, "source": "Industry case studies"},
            ],
        },
        "synthesis:Synthesizer": {
            "key_insight": "Phased migration with non-critical workloads first reduces risk",
            "evidence": [
                {"claim": "Phased migration recommended", "confidence": 0.82, "source": "Synthesis of all agent outputs"},
            ],
        },
        "validation:Validator": {
            "cross_validation": "Analysis is sound but cost projection for years 2-3 needs refinement",
            "confidence": 0.78,
            "gaps_identified": ["Cost projection for year 2-3"],
            "evidence": [
                {"claim": "Analysis sound, cost projection needs refinement", "confidence": 0.78, "source": "Cross-validation report"},
            ],
        },
    }


def main():
    global passed, failed
    print("=" * 60)
    print("ORCHESTRATOR TEST \u2014 MODE TOPIC tracer bullet")
    print("=" * 60)

    schemas = load_schemas()
    topic_schema = schemas.get("topic-analysis.schema.json")
    if not topic_schema:
        check("topic-analysis.schema.json exists", False, "schema file not found")
        print("\nResult: 0 passed, 1 failed")
        return 1

    handoff = make_handoff_brief()
    fake_outputs = make_fake_outputs()

    # ── Test 1: Fake agent runner interface ──
    print("\n[1] FakeAgentRunner implements AgentRunner interface")
    fake = FakeAgentRunner(fake_outputs)
    check("FakeAgentRunner is AgentRunner", isinstance(fake, AgentRunner))
    output = fake.run("Researcher", "research", {"topic": "test"})
    check("run returns dict from outputs", isinstance(output, dict))
    check("correct output retrieved", output["findings"]["market_trends"] == "Cloud adoption growing 35% YoY")
    check("calls tracked", len(fake.calls) == 1)

    # ── Test 2: Orchestrator creation ──
    print("\n[2] XThinkingOrchestrator creation")
    tracker = EvidenceTracker()
    orchestrator = XThinkingOrchestrator(mode="topic", agent_runner=fake, evidence_tracker=tracker)
    check("orchestrator created", isinstance(orchestrator, XThinkingOrchestrator))
    check("mode set correctly", orchestrator.mode == "topic")
    check("agent_runner assigned", orchestrator.agent_runner is fake)
    check("evidence_tracker assigned", orchestrator.evidence_tracker is tracker)

    # ── Test 3: Full pipeline execution ──
    print("\n[3] Full pipeline execution")
    fake = FakeAgentRunner(fake_outputs)
    orchestrator = XThinkingOrchestrator(mode="topic", agent_runner=fake, evidence_tracker=EvidenceTracker())
    result = orchestrator.execute(handoff)

    check("result is dict", isinstance(result, dict))
    check("has analysis_id", "analysis_id" in result)
    check("topic matches handoff context", result.get("topic") == "FinTech industry in Southeast Asia")
    check("mode is topic", result.get("mode") == "topic")

    # ── Test 4: Phases are correct ──
    print("\n[4] Phase structure")
    phases = result.get("phases", [])
    check("5 phases in output", len(phases) == 5)
    expected_phases = [
        ("research", "Researcher"),
        ("thinking", "Explicit Thinker"),
        ("thinking", "Value Chain Analyst"),
        ("synthesis", "Synthesizer"),
        ("validation", "Validator"),
    ]
    for i, (expected_phase, expected_agent) in enumerate(expected_phases):
        check(f"phase {i+1}: {expected_agent}", 
              phases[i]["phase"] == expected_phase and phases[i]["agent"] == expected_agent,
              f"got {phases[i]['phase']}/{phases[i]['agent']}")
        check(f"phase {i+1} has output", isinstance(phases[i].get("output"), dict))

    # ── Test 5: Evidence tracking applied ──
    print("\n[5] Evidence tracking")
    check("has evidence list", "evidence" in result and len(result["evidence"]) > 0)
    check("has confidence_score", "confidence_score" in result)
    check("confidence_score in [0,1]", 0 <= result["confidence_score"] <= 1)
    check("has need_review", "need_review" in result)
    check("need_review is bool", isinstance(result["need_review"], bool))
    check("has insights", "insights" in result and len(result["insights"]) > 0)
    for ins in result["insights"]:
        check("insight has claim/evidence/source", 
              "claim" in ins and "evidence" in ins and "source" in ins)

    # ── Test 6: Schema compliance ──
    print("\n[6] Schema compliance")
    errs = validate(topic_schema, result)
    check("output validates against topic-analysis.schema.json", not errs,
          "; ".join(e.message for e in errs[:3]))

    # ── Test 7: All agents called ──
    print("\n[7] Agent invocation order")
    expected_calls = [
        "research:Researcher",
        "thinking:Explicit Thinker",
        "thinking:Value Chain Analyst",
        "synthesis:Synthesizer",
        "validation:Validator",
    ]
    check("all 5 agents called", len(fake.calls) == 5, f"called {len(fake.calls)} agents")
    for i, (key, _) in enumerate(fake.calls):
        check(f"call {i+1}: {expected_calls[i]}", key == expected_calls[i],
              f"got {key}, expected {expected_calls[i]}")

    # ── Test 8: Custom analysis_id ──
    print("\n[8] Custom analysis_id")
    handoff2 = make_handoff_brief()
    fake2 = FakeAgentRunner(fake_outputs)
    orch2 = XThinkingOrchestrator(mode="topic", agent_runner=fake2, evidence_tracker=EvidenceTracker())
    result2 = orch2.execute(handoff2, analysis_id="custom-001")
    check("custom analysis_id used", result2.get("analysis_id") == "custom-001")

    # ── Test 9: Empty input edge case ──
    print("\n[9] Empty/invalid input handling")
    fake3 = FakeAgentRunner({})
    orch3 = XThinkingOrchestrator(mode="topic", agent_runner=fake3, evidence_tracker=EvidenceTracker())
    try:
        result3 = orch3.execute({"request_id": "empty"})
        check("executes with minimal input", True)
        check("confidence_score defaults to 0", result3.get("confidence_score") == 0.0)
    except Exception as e:
        check("handles empty input gracefully", False, str(e))

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
