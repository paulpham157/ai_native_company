#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "script"))

from context_provider import ContextProvider, KBContextProvider
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


SKILL_DIR = Path(__file__).resolve().parent.parent


def make_handoff(industry="FinTech in Southeast Asia"):
    return {
        "request_id": "req-001",
        "analysis_type": "topic",
        "context": {
            "charter_summary": "Digital transformation charter",
            "okr_summary": "OKR: 30% revenue from digital channels",
            "industry_context": industry,
        },
        "evidence": [],
        "confidence_score": 0.85,
        "need_review": False,
    }


def main():
    global passed, failed
    print("=" * 60)
    print("CONTEXT PROVIDER TEST \u2014 vibe-xthinking-orchestrator")
    print("=" * 60)

    # ── Test 1: ContextProvider interface ──
    print("\n[1] ContextProvider interface")
    try:
        base = ContextProvider()
        base.enrich({}, "research", "Researcher")
        check("ContextProvider base raises NotImplementedError", False, "should raise")
    except NotImplementedError:
        check("ContextProvider.enrich raises NotImplementedError", True)
    except Exception as e:
        check(f"ContextProvider.enrich raises NotImplementedError", False, f"got {type(e).__name__}: {e}")

    # ── Test 2: KBContextProvider default skill_dir auto-discovery ──
    print("\n[2] KBContextProvider default skill_dir auto-discovery")
    auto_provider = KBContextProvider()
    auto_result = auto_provider.enrich(make_handoff("Tech startup in Singapore"), "research", "Researcher")
    kb_docs = auto_result.get("kb_docs", {})
    has_evidence_rubric = any("evidence-rubric" in str(k) for k in kb_docs.keys())
    check("default constructor loads evidence-rubric.md", has_evidence_rubric)

    # ── Test 3: Industry template selection ──
    print("\n[3] Industry template selection")
    provider = KBContextProvider(skill_dir=SKILL_DIR)

    tech_handoff = make_handoff("Tech startup in Singapore")
    tech_result = provider.enrich(tech_handoff, "research", "Researcher")
    check("tech-startup template found", "industry_template" in tech_result)
    check("tech-startup template content has Market Overview",
          tech_result["industry_template"] and "Market Overview" in tech_result["industry_template"])

    ecom_handoff = make_handoff("Ecommerce platform in Vietnam")
    ecom_result = provider.enrich(ecom_handoff, "research", "Researcher")
    check("ecommerce template found", "industry_template" in ecom_result)
    check("ecommerce template has relevant content",
          ecom_result["industry_template"] and "Market Overview" in ecom_result["industry_template"])

    consult_handoff = make_handoff("Management consulting for banks")
    consult_result = provider.enrich(consult_handoff, "research", "Researcher")
    check("consulting template found", "industry_template" in consult_result)

    unknown_handoff = make_handoff("Quantum computing research")
    unknown_result = provider.enrich(unknown_handoff, "research", "Researcher")
    check("unknown industry returns None template",
          unknown_result.get("industry_template") is None)

    # ── Test 4: Phase-specific KB loading ──
    print("\n[4] Phase-specific KB loading")
    research_ctx = provider.enrich(make_handoff(), "research", "Researcher")
    kb = research_ctx.get("kb_docs", {})
    check("research phase loads evidence-rubric.md", "evidence-rubric.md" in kb)
    check("research phase loads quality-standards.md", "quality-standards.md" in kb)

    thinking_ctx = provider.enrich(make_handoff(), "thinking", "Explicit Thinker")
    kb2 = thinking_ctx.get("kb_docs", {})
    check("thinking phase loads analysis-frameworks.md", "analysis-frameworks.md" in kb2)
    check("thinking phase loads thinking-anti-patterns.md", "thinking-anti-patterns.md" in kb2)

    validation_ctx = provider.enrich(make_handoff(), "validation", "Validator")
    kb3 = validation_ctx.get("kb_docs", {})
    check("validation phase loads evidence-tracking-rubric.md", "evidence-tracking-rubric.md" in kb3)

    # ── Test 5: KB content is non-empty ──
    print("\n[5] KB content quality")
    for phase_name, ctx in [("research", research_ctx), ("thinking", thinking_ctx), ("validation", validation_ctx)]:
        for doc_name, content in ctx.get("kb_docs", {}).items():
            check(f"{phase_name}: {doc_name} has content", len(content) > 50,
                  f"only {len(content)} chars")

    # ── Test 6: Provider enriches orchestrator agent context ──
    print("\n[6] Orchestrator integration — context passed to agent")
    captured_contexts = {}

    class CapturingRunner(FakeAgentRunner):
        def run(self, agent_name, phase, context):
            captured_contexts[f"{phase}:{agent_name}"] = context
            return {"evidence": []}

    provider = KBContextProvider(skill_dir=SKILL_DIR)
    orch = XThinkingOrchestrator(
        mode="topic",
        agent_runner=CapturingRunner({}),
        context_provider=provider,
        checkpoint=None,
    )
    orch.execute(make_handoff())

    for key, ctx in captured_contexts.items():
        check(f"{key} has kb_docs in context", "kb_docs" in ctx,
              f"missing kb_docs in {key}")
        check(f"{key} has industry_template in context", "industry_template" in ctx,
              f"missing industry_template in {key}")

    # ── Test 7: Missing KB files — graceful degradation ──
    print("\n[7] Graceful degradation with missing files")
    fake_dir = Path("/tmp/nonexistent-skill-dir")
    degraded = KBContextProvider(skill_dir=fake_dir)
    result = degraded.enrich(make_handoff(), "research", "Researcher")
    check("no crash with missing KB dir", True)
    check("kb_docs is empty dict", result.get("kb_docs") == {})
    check("industry_template is None", result.get("industry_template") is None)

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
