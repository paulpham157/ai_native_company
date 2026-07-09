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

    # ── Test 3: Orchestrator rejects invalid mode ──
    print("\n[3] Orchestrator rejects invalid mode")
    try:
        XThinkingOrchestrator(mode="invalid-mode", agent_runner=fake, evidence_tracker=tracker)
        check("invalid mode raises ValueError", False, "expected ValueError")
    except ValueError as e:
        check("invalid mode raises ValueError", True)
        check("error message mentions mode", "mode" in str(e).lower(),
              f"message: {e}")

    # ── Test 4: Full pipeline execution ──
    print("\n[3] Full pipeline execution")
    fake = FakeAgentRunner(fake_outputs)
    orchestrator = XThinkingOrchestrator(mode="topic", agent_runner=fake, evidence_tracker=EvidenceTracker())
    result = orchestrator.execute(handoff)

    check("result is dict", isinstance(result, dict))
    check("has analysis_id", "analysis_id" in result)
    check("topic matches handoff context", result.get("topic") == "FinTech industry in Southeast Asia")
    check("mode is topic", result.get("mode") == "topic")

    # ── Test 5: Phases are correct ──
    print("\n[5] Phase structure")
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
        check("insight has claim/evidence_source/agent", 
              "claim" in ins and "evidence_source" in ins and "agent" in ins)

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

    # ── Test 10: Problem mode execution (tracer bullet) ──
    print("\n[10] Problem mode execution")
    handoff_problem = {
        "request_id": "req-problem-001",
        "analysis_type": "problem",
        "context": {
            "industry_context": "High customer churn rate in B2B SaaS",
        },
        "evidence": [],
        "confidence_score": 0.8,
        "need_review": False,
    }

    fake_problem_outputs = {
        "analysis:Problem Analyst": {
            "framework": "5-whys",
            "root_causes": [{"cause": "Poor onboarding", "level": 1, "category": "process"}],
            "recommendations": ["Improve onboarding with milestones"],
            "evidence": [
                {"claim": "60% of churned customers cite poor onboarding", "confidence": 0.85, "source": "Exit survey 2025"},
            ],
        },
    }
    fake_problem = FakeAgentRunner(fake_problem_outputs)
    orch_p = XThinkingOrchestrator(mode="problem", agent_runner=fake_problem, evidence_tracker=EvidenceTracker())
    result_p = orch_p.execute(handoff_problem)

    check("result is dict", isinstance(result_p, dict))
    check("has analysis_id", "analysis_id" in result_p)
    check("problem matches handoff context", result_p.get("problem") == "High customer churn rate in B2B SaaS")
    check("mode is problem", result_p.get("mode") == "problem")
    check("has framework", result_p.get("framework") == "5-whys")
    check("has root_causes", len(result_p.get("root_causes", [])) == 1)
    check("root_cause has cause/level", result_p["root_causes"][0]["cause"] == "Poor onboarding" and result_p["root_causes"][0]["level"] == 1)
    check("has recommendations", len(result_p.get("recommendations", [])) == 1)
    check("has evidence list", "evidence" in result_p and len(result_p["evidence"]) > 0)
    check("has confidence_score", "confidence_score" in result_p)
    check("confidence_score in [0,1]", 0 <= result_p["confidence_score"] <= 1)
    check("has need_review", "need_review" in result_p)
    check("need_review is bool", isinstance(result_p["need_review"], bool))
    check("has insights", "insights" in result_p and len(result_p["insights"]) > 0)
    for ins in result_p["insights"]:
        check("insight has claim/evidence_source/agent",
              "claim" in ins and "evidence_source" in ins and "agent" in ins)

    # ── Test 11: Problem mode schema compliance ──
    print("\n[11] Problem mode schema compliance")
    problem_schema = schemas.get("problem-analysis.schema.json")
    if problem_schema:
        errs = validate(problem_schema, result_p)
        check("output validates against problem-analysis.schema.json", not errs,
              "; ".join(e.message for e in errs[:3]))
    else:
        check("problem-analysis.schema.json exists", False)

    # ── Test 12: Problem mode custom analysis_id ──
    print("\n[12] Problem mode custom analysis_id")
    handoff_p2 = {
        "request_id": "req-problem-002",
        "analysis_type": "problem",
        "context": {"industry_context": "Test problem"},
        "evidence": [],
        "confidence_score": 0.8,
        "need_review": False,
    }
    fake_p2 = FakeAgentRunner(fake_problem_outputs)
    orch_p2 = XThinkingOrchestrator(mode="problem", agent_runner=fake_p2, evidence_tracker=EvidenceTracker())
    result_p2 = orch_p2.execute(handoff_p2, analysis_id="problem-custom-001")
    check("custom analysis_id used", result_p2.get("analysis_id") == "problem-custom-001")

    # ── Test 13: Problem mode empty/minimal input ──
    print("\n[13] Problem mode empty/minimal input")
    fake_empty = FakeAgentRunner({})
    orch_empty = XThinkingOrchestrator(mode="problem", agent_runner=fake_empty, evidence_tracker=EvidenceTracker())
    try:
        result_empty = orch_empty.execute({"request_id": "empty-problem"})
        check("executes with minimal problem input", True)
        check("problem falls back to Unknown", result_empty.get("problem") == "Unknown problem")
        check("framework defaults to 5-whys", result_empty.get("framework") == "5-whys")
        check("empty root_causes", len(result_empty.get("root_causes", [])) == 0)
        check("confidence_score defaults to 0", result_empty.get("confidence_score") == 0.0)
        check("insights is empty list", result_empty.get("insights") == [])
    except Exception as e:
        check("handles empty problem input gracefully", False, str(e))

    # ── Test 14: Invalid mode still rejected ──
    print("\n[14] Invalid mode rejected")
    try:
        XThinkingOrchestrator(mode="invalid-mode", agent_runner=FakeAgentRunner({}), evidence_tracker=EvidenceTracker())
        check("invalid mode raises ValueError", False, "expected ValueError")
    except ValueError as e:
        check("invalid mode raises ValueError", True)
        check("error message mentions mode", "mode" in str(e).lower(),
              f"message: {e}")

    # ── Test 15: Decision mode execution ──
    print("\n[15] Decision mode execution")
    handoff_decision = {
        "request_id": "req-decision-001",
        "analysis_type": "decision",
        "context": {
            "industry_context": "Build vs buy for customer analytics platform",
        },
        "evidence": [],
        "confidence_score": 0.8,
        "need_review": False,
    }

    fake_decision_outputs = {
        "analysis:Decision Analyst": {
            "framework": "rice",
            "options": [
                {"name": "Build in-house", "scores": {"reach": 3, "impact": 4, "effort": 2}, "total": 24},
                {"name": "Buy SaaS", "scores": {"reach": 5, "impact": 3, "effort": 4}, "total": 60},
            ],
            "recommendation": "Buy SaaS scores highest on RICE",
            "evidence": [
                {"claim": "SaaS faster time-to-market", "confidence": 0.85, "source": "Vendor analysis"},
            ],
        },
    }
    fake_decision = FakeAgentRunner(fake_decision_outputs)
    orch_d = XThinkingOrchestrator(mode="decision", agent_runner=fake_decision, evidence_tracker=EvidenceTracker())
    result_d = orch_d.execute(handoff_decision)

    check("result is dict", isinstance(result_d, dict))
    check("has analysis_id", "analysis_id" in result_d)
    check("decision matches handoff context", result_d.get("decision") == "Build vs buy for customer analytics platform")
    check("mode is decision", result_d.get("mode") == "decision")
    check("has framework", result_d.get("framework") == "rice")
    check("has options", len(result_d.get("options", [])) == 2)
    check("option has name/scores", "name" in result_d["options"][0] and "scores" in result_d["options"][0])
    check("option has total", "total" in result_d["options"][0])
    check("has recommendation", result_d.get("recommendation") == "Buy SaaS scores highest on RICE")
    check("has evidence list", "evidence" in result_d and len(result_d["evidence"]) > 0)
    check("has confidence_score", "confidence_score" in result_d)
    check("confidence_score in [0,1]", 0 <= result_d["confidence_score"] <= 1)
    check("has need_review", "need_review" in result_d)
    check("need_review is bool", isinstance(result_d["need_review"], bool))
    check("has insights", "insights" in result_d and len(result_d["insights"]) > 0)
    for ins in result_d["insights"]:
        check("insight has claim/evidence_source/agent",
              "claim" in ins and "evidence_source" in ins and "agent" in ins)

    # ── Test 16: Decision mode schema compliance ──
    print("\n[16] Decision mode schema compliance")
    decision_schema = schemas.get("decision-analysis.schema.json")
    if decision_schema:
        errs = validate(decision_schema, result_d)
        check("output validates against decision-analysis.schema.json", not errs,
              "; ".join(e.message for e in errs[:3]))
    else:
        check("decision-analysis.schema.json exists", False)

    # ── Test 17: Decision mode custom analysis_id ──
    print("\n[17] Decision mode custom analysis_id")
    handoff_d2 = {
        "request_id": "req-decision-002",
        "analysis_type": "decision",
        "context": {"industry_context": "Test decision"},
        "evidence": [],
        "confidence_score": 0.8,
        "need_review": False,
    }
    fake_d2 = FakeAgentRunner(fake_decision_outputs)
    orch_d2 = XThinkingOrchestrator(mode="decision", agent_runner=fake_d2, evidence_tracker=EvidenceTracker())
    result_d2 = orch_d2.execute(handoff_d2, analysis_id="decision-custom-001")
    check("custom analysis_id used", result_d2.get("analysis_id") == "decision-custom-001")

    # ── Test 18: Decision mode empty/minimal input ──
    print("\n[18] Decision mode empty/minimal input")
    fake_empty_d = FakeAgentRunner({})
    orch_empty_d = XThinkingOrchestrator(mode="decision", agent_runner=fake_empty_d, evidence_tracker=EvidenceTracker())
    try:
        result_empty = orch_empty_d.execute({"request_id": "empty-decision"})
        check("executes with minimal decision input", True)
        check("decision falls back to Unknown", result_empty.get("decision") == "Unknown decision")
        check("framework defaults to eisenhower", result_empty.get("framework") == "eisenhower")
        check("empty options", len(result_empty.get("options", [])) == 0)
        check("empty recommendation", result_empty.get("recommendation") == "")
        check("confidence_score defaults to 0", result_empty.get("confidence_score") == 0.0)
        check("insights is empty list", result_empty.get("insights") == [])
    except Exception as e:
        check("handles empty decision input gracefully", False, str(e))

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
