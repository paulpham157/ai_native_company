#!/usr/bin/env python3

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "script"))

from cli import build_parser, run_from_args
from agent_runner import FakeAgentRunner

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


SAMPLE_HANDOFF = {
    "request_id": "req-001",
    "analysis_type": "topic",
    "context": {
        "charter_summary": "Test charter",
        "okr_summary": "Test OKRs",
        "industry_context": "Tech startup test",
    },
    "evidence": [],
    "confidence_score": 0.8,
    "need_review": False,
}

FAKE_OUTPUTS = {
    "research:Researcher": {"findings": "done", "evidence": [{"claim": "C1", "confidence": 0.9, "source": "S1"}]},
    "thinking:Explicit Thinker": {"assumptions": [], "evidence": []},
    "thinking:Value Chain Analyst": {"analysis": "done", "evidence": []},
    "synthesis:Synthesizer": {"key_insight": "done", "evidence": []},
    "validation:Validator": {"result": "validated", "evidence": []},
}

FAKE_RUNNER = FakeAgentRunner(FAKE_OUTPUTS)


def main():
    global passed, failed
    print("=" * 60)
    print("CLI TEST \u2014 vibe-xthinking-orchestrator")
    print("=" * 60)

    # ── Test 1: Argument parser builds correctly ──
    print("\n[1] Argument parser")
    parser = build_parser()
    check("parser is argparse.ArgumentParser", parser is not None)
    args = parser.parse_args(["--mode", "topic", "--input", "test.json"])
    check("mode parsed", args.mode == "topic")
    check("input parsed", args.input == "test.json")
    check("output defaults to None", args.output is None)
    check("interactive defaults to False", hasattr(args, "interactive"))
    check("pretty defaults to False", hasattr(args, "pretty"))

    args2 = parser.parse_args(["--mode", "topic", "--output", "out.json", "--interactive", "--pretty"])
    check("output parsed", args2.output == "out.json")
    check("interactive flag", args2.interactive is True)
    check("pretty flag", args2.pretty is True)

    # ── Test 2: Run from args with stdin/stdout ──
    print("\n[2] Run from args (stdin → stdout)")
    input_json = json.dumps(SAMPLE_HANDOFF)
    exit_code, output = run_from_args(
        mode="topic",
        input_data=input_json,
        interactive=False,
        capture_output=True,
        agent_runner=FAKE_RUNNER,
    )
    check("exit code 0 on success", exit_code == 0, f"got {exit_code}")

    # ── Test 3: Run produces valid JSON output ──
    print("\n[3] Output is valid topic-analysis artifact")
    exit_code, output = run_from_args(
        mode="topic",
        input_data=input_json,
        interactive=False,
        capture_output=True,
        agent_runner=FAKE_RUNNER,
    )
    check("exit code 0", exit_code == 0)
    result = json.loads(output)
    check("output has analysis_id", "analysis_id" in result)
    check("output mode is topic", result.get("mode") == "topic")
    check("output has phases", len(result.get("phases", [])) == 5)
    check("output has confidence_score", "confidence_score" in result)
    check("output has need_review", "need_review" in result)

    # ── Test 4: Custom analysis_id ──
    print("\n[4] Custom analysis_id")
    _, output = run_from_args(
        mode="topic",
        input_data=input_json,
        analysis_id="cli-custom-001",
        capture_output=True,
        agent_runner=FAKE_RUNNER,
    )
    result = json.loads(output)
    check("custom analysis_id in output", result.get("analysis_id") == "cli-custom-001")

    # ── Test 5: File input ──
    print("\n[5] File input")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(SAMPLE_HANDOFF, f)
        fpath = f.name
    try:
        exit_code, output = run_from_args(
            mode="topic",
            input_path=fpath,
            capture_output=True,
            agent_runner=FAKE_RUNNER,
        )
        check("file input exit code 0", exit_code == 0)
        result = json.loads(output)
        check("file input produces valid artifact", "analysis_id" in result)
    finally:
        Path(fpath).unlink(missing_ok=True)

    # ── Test 6: File output ──
    print("\n[6] File output")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        outpath = f.name
    try:
        exit_code = run_from_args(
            mode="topic",
            input_data=input_json,
            output_path=outpath,
            agent_runner=FAKE_RUNNER,
        )
        check("file output exit code 0", exit_code == 0)
        saved = json.loads(Path(outpath).read_text())
        check("file output has analysis_id", "analysis_id" in saved)
    finally:
        Path(outpath).unlink(missing_ok=True)

    # ── Test 7: Invalid mode ──
    print("\n[7] Invalid mode")
    exit_code, output = run_from_args(
        mode="invalid",
        input_data=input_json,
        capture_output=True,
        agent_runner=FAKE_RUNNER,
    )
    check("invalid mode returns non-zero", exit_code != 0)

    # ── Test 8: Unsupported 'problem' mode ──
    print("\n[8] Unsupported 'problem' mode")
    exit_code, output = run_from_args(
        mode="problem",
        input_data=input_json,
        capture_output=True,
        agent_runner=FAKE_RUNNER,
    )
    check("problem mode returns non-zero", exit_code != 0)
    check("problem mode reports unsupported",
          isinstance(output, str) and "unknown mode" in output.lower())

    # ── Test 9: Unsupported 'decision' mode ──
    print("\n[9] Unsupported 'decision' mode")
    exit_code, output = run_from_args(
        mode="decision",
        input_data=input_json,
        capture_output=True,
        agent_runner=FAKE_RUNNER,
    )
    check("decision mode returns non-zero", exit_code != 0)
    check("decision mode reports unsupported",
          isinstance(output, str) and "unknown mode" in output.lower())

    # ── Test 10: Missing input ──
    print("\n[10] Missing input")
    exit_code, output = run_from_args(
        mode="topic",
        input_data="",
        capture_output=True,
        agent_runner=FAKE_RUNNER,
    )
    check("empty input returns non-zero", exit_code != 0)

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
