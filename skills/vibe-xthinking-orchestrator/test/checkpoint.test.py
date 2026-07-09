#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "script"))

from checkpoint import Checkpoint, CheckpointResult, AutoCheckpoint
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


def make_fake_outputs():
    return {
        "research:Researcher": {"findings": "research done", "evidence": []},
        "thinking:Explicit Thinker": {"assumptions": [], "evidence": []},
        "thinking:Value Chain Analyst": {"analysis": "done", "evidence": []},
        "synthesis:Synthesizer": {"key_insight": "synthesis done", "evidence": []},
        "validation:Validator": {"result": "validated", "evidence": []},
    }


class FakeCheckpoint(Checkpoint):
    def __init__(self, results=None):
        self.results = results if results else {}
        self.calls = []

    def pause(self, phase, output, context=None):
        self.calls.append((phase, output, context))
        key = phase
        if key in self.results:
            return self.results[key]
        return CheckpointResult("continue")


def main():
    global passed, failed
    print("=" * 60)
    print("CHECKPOINT TEST \u2014 vibe-xthinking-orchestrator")
    print("=" * 60)

    outputs = make_fake_outputs()
    handoff = make_handoff()

    # ── Test 1: CheckpointResult creation ──
    print("\n[1] CheckpointResult creation")
    cr = CheckpointResult("continue")
    check("action set correctly", cr.action == "continue")
    check("feedback defaults to empty", cr.feedback == "")

    cr2 = CheckpointResult("revise", "Need more data")
    check("revise action", cr2.action == "revise")
    check("feedback stored", cr2.feedback == "Need more data")

    # ── Test 2: Checkpoint interface — AutoCheckpoint ──
    print("\n[2] Checkpoint interface bounds")
    auto = AutoCheckpoint()
    check("AutoCheckpoint is Checkpoint", isinstance(auto, Checkpoint))
    result = auto.pause("research", {"data": "test"})
    check("AutoCheckpoint always continues", result.action == "continue")
    check("AutoCheckpoint has no feedback", result.feedback == "")

    fake_cp = FakeCheckpoint({})
    check("FakeCheckpoint is Checkpoint", isinstance(fake_cp, Checkpoint))
    result = fake_cp.pause("research", {"data": "test"})
    check("FakeCheckpoint defaults to continue", result.action == "continue")

    # ── Test 3: Orchestrator calls checkpoints at correct phases ──
    print("\n[3] Checkpoint invocation points")
    cp = FakeCheckpoint({})
    orch = XThinkingOrchestrator(
        mode="topic",
        agent_runner=FakeAgentRunner(outputs),
        checkpoint=cp,
    )
    orch.execute(handoff)
    checkpoint_phases = [call[0] for call in cp.calls]
    check("checkpoint called after research", "research" in checkpoint_phases)
    check("checkpoint called after thinking", "thinking" in checkpoint_phases)
    check("exactly 2 checkpoints", len(cp.calls) == 2, f"got {len(cp.calls)}")

    # ── Test 4: Checkpoint receives phase output ──
    print("\n[4] Checkpoint receives correct data")
    cp2 = FakeCheckpoint({})
    orch2 = XThinkingOrchestrator(
        mode="topic",
        agent_runner=FakeAgentRunner(outputs),
        checkpoint=cp2,
    )
    orch2.execute(handoff)
    for phase_name, output, context in cp2.calls:
        check(f"checkpoint {phase_name} receives phase results",
              "phase_results" in (context or {}),
              f"missing phase_results in {phase_name} context")
        check(f"checkpoint {phase_name} receives handoff",
              "handoff" in (context or {}),
              f"missing handoff in {phase_name} context")
        check(f"checkpoint {phase_name} receives dict output",
              isinstance(output, dict),
              f"output type: {type(output)}")

    # ── Test 5: Pipeline completes with auto-approve ──
    print("\n[5] Pipeline completion with AutoCheckpoint")
    auto = AutoCheckpoint()
    orch3 = XThinkingOrchestrator(
        mode="topic",
        agent_runner=FakeAgentRunner(outputs),
        checkpoint=auto,
    )
    result = orch3.execute(handoff)
    check("artifact produced with AutoCheckpoint", "analysis_id" in result)
    check("all 5 phases present", len(result.get("phases", [])) == 5)

    # ── Test 6: No checkpoint orchestrator still works ──
    print("\n[6] No checkpoint (backward compat)")
    orch4 = XThinkingOrchestrator(
        mode="topic",
        agent_runner=FakeAgentRunner(outputs),
        checkpoint=None,
    )
    result = orch4.execute(handoff)
    check("artifact produced without checkpoint", "analysis_id" in result)
    check("all 5 phases present", len(result.get("phases", [])) == 5)

    # ── Test 7: Revise with feedback re-runs phase ──
    print("\n[7] Revise triggers phase re-execution")
    revise_cp = FakeCheckpoint({
        "research": CheckpointResult("revise", "Add competitor analysis"),
        "thinking": CheckpointResult("continue"),
    })
    runner = FakeAgentRunner(outputs)
    orch5 = XThinkingOrchestrator(
        mode="topic",
        agent_runner=runner,
        checkpoint=revise_cp,
    )
    orch5.execute(handoff)
    research_calls = [c for c in runner.calls if c[0] == "research:Researcher"]
    check("researcher called twice on revise", len(research_calls) == 2,
          f"called {len(research_calls)} times")
    second_context = research_calls[1][1]
    check("feedback passed in revised run", "feedback" in second_context,
          "missing feedback in second call context")
    check("feedback content preserved",
          second_context.get("feedback") == "Add competitor analysis")

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
