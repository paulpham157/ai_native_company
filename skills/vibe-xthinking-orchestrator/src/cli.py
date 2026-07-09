import argparse
import json
import sys
from pathlib import Path

from agent_runner import AgentRunner
from checkpoint import AutoCheckpoint
from context_provider import KBContextProvider
from evidence_tracker import EvidenceTracker
from evidence_validator import EvidenceValidator
from orchestrator import XThinkingOrchestrator


def build_parser():
    parser = argparse.ArgumentParser(
        description="vibe-xthinking-orchestrator — Multi-agent analysis pipeline",
    )
    parser.add_argument("--mode", required=True, choices=["topic"],
                        help="Analysis mode (only topic supported)")
    parser.add_argument("--input", help="Input JSON file (default: stdin)")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    parser.add_argument("--analysis-id", help="Custom analysis ID")
    parser.add_argument("--interactive", action="store_true",
                        help="Enable interactive checkpoints")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print JSON output")
    return parser


def run_from_args(mode, input_data=None, input_path=None, output_path=None,
                  analysis_id=None, interactive=False, pretty=False,
                  capture_output=False, agent_runner=None):
    try:
        if input_data is not None:
            handoff = json.loads(input_data) if input_data else None
        elif input_path:
            handoff = json.loads(Path(input_path).read_text())
        else:
            handoff = json.loads(sys.stdin.read())

        if not handoff:
            return _exit("Empty input", capture_output, 1)

        if agent_runner is None:
            return _exit("Agent runner is required — not provided", capture_output, 1)

        runner = agent_runner
        tracker = EvidenceTracker()
        validator = EvidenceValidator()
        provider = KBContextProvider()

        checkpoint = None
        if not interactive:
            checkpoint = AutoCheckpoint()

        orch = XThinkingOrchestrator(
            mode=mode,
            agent_runner=runner,
            evidence_tracker=tracker,
            checkpoint=checkpoint,
            context_provider=provider,
            evidence_validator=validator,
        )

        result = orch.execute(handoff, analysis_id=analysis_id)

        output = json.dumps(result, indent=2 if pretty else None)

        if output_path:
            Path(output_path).write_text(output)
        elif capture_output:
            return 0, output
        else:
            print(output)

        return 0 if not capture_output else (0, output)

    except Exception as e:
        msg = f"Error: {e}"
        return _exit(msg, capture_output, 1)


def _exit(msg, capture_output, code):
    if capture_output:
        return code, msg
    print(msg, file=sys.stderr)
    return code


def main():
    parser = build_parser()
    args = parser.parse_args()
    exit_code = run_from_args(
        mode=args.mode,
        input_path=args.input,
        output_path=args.output,
        analysis_id=args.analysis_id,
        interactive=args.interactive,
        pretty=args.pretty,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
