#!/usr/bin/env python3

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from test_helpers import get_skill_dir, check, summary as _summary, passed, failed


def main():
    global passed, failed
    print("=" * 60)
    print("TEST — ReviewOrchestrator quick mode")
    print("=" * 60)

    from orchestrator import ReviewOrchestrator

    orch = ReviewOrchestrator()

    print("\n[1] Quick mode — markdown artifact")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Test Document\n\nThis is a test.\n")
        tmp_path = f.name

    try:
        result = orch.review(tmp_path, mode="quick")

        check("result is a dict", isinstance(result, dict))
        check("artifact_path matches input", result.get("artifact_path") == tmp_path)
        check("artifact_type is 'markdown'", result.get("artifact_type") == "markdown")
        check("issues is a list", isinstance(result.get("issues"), list))
        check("evidence is a list", isinstance(result.get("evidence"), list))
        check("confidence_score is a float 0-1",
               isinstance(result.get("confidence_score"), (int, float)) and 0 <= result["confidence_score"] <= 1)
        check("need_review is a bool", isinstance(result.get("need_review"), bool))
        check("summary is a string", isinstance(result.get("summary"), str))
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    print("\n[2] Quick mode — unsupported artifact type")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("some text\n")
        tmp_path = f.name

    try:
        result = orch.review(tmp_path, mode="quick")

        check("artifact_type is 'unsupported'", result.get("artifact_type") == "unsupported")
        check("need_review is true for unsupported", result.get("need_review") is True)
        check("summary mentions unsupported", "unsupported" in result.get("summary", "").lower())
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    print("\n[3] Rules-based review — missing title warning")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("Some text without a title.\n")
        tmp_path = f.name

    try:
        result = orch.review(tmp_path, mode="quick")
        issues = result.get("issues", [])
        title_warnings = [i for i in issues if "title" in i.get("message", "").lower()]
        check("issues contains title warning", len(title_warnings) >= 1)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    print("\n[4] Rules-based review — valid markdown passes")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Valid Title\n\nContent.\n")
        tmp_path = f.name

    try:
        result = orch.review(tmp_path, mode="quick")
        issues = result.get("issues", [])
        title_warnings = [i for i in issues if "title" in i.get("message", "").lower()]
        check("no title warning for valid doc", len(title_warnings) == 0)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    print("\n[5] Schema validation — malformed JSON flagged")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{invalid json here}\n')
        tmp_path = f.name

    try:
        result = orch.review(tmp_path, mode="quick")
        issues = result.get("issues", [])
        parse_errors = [i for i in issues if "parse" in i.get("message", "").lower()]
        check("malformed JSON gets parse error", len(parse_errors) >= 1)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    print("\n[6] Schema validation — valid JSON passes")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"name": "test", "version": 1}\n')
        tmp_path = f.name

    try:
        result = orch.review(tmp_path, mode="quick")
        parse_errors = [i for i in result.get("issues", []) if "parse" in i.get("message", "").lower()]
        check("no parse errors for valid JSON", len(parse_errors) == 0)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    print("\n[7] Schema validation — valid YAML passes")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("name: test\nversion: 1\n")
        tmp_path = f.name

    try:
        result = orch.review(tmp_path, mode="quick")
        check("artifact_type is 'yaml'", result.get("artifact_type") == "yaml")
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    print("\n[8] Full mode — includes quality rubric scores")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Good Document\n\nClear and complete content.\n")
        tmp_path = f.name

    try:
        result = orch.review(tmp_path, mode="full")
        check("artifact_type is 'markdown'", result.get("artifact_type") == "markdown")
        check("quality_scores is a dict", isinstance(result.get("quality_scores"), dict))
        for dim in ["clarity", "completeness", "accuracy", "consistency", "actionability"]:
            check(f"quality_scores includes '{dim}'", dim in result.get("quality_scores", {}))
            score = result["quality_scores"][dim]
            check(f"  '{dim}' score is 0-1", isinstance(score, (int, float)) and 0 <= score <= 1)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    print("\n[9] Output validates against review-result.schema.json")
    schema_path = get_skill_dir() / "schema" / "review-result.schema.json"
    check("schema file exists", schema_path.is_file())
    if schema_path.is_file():
        import json as json_mod
        schema = json_mod.loads(schema_path.read_text())

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Hello\n")
            tmp_path = f.name

        try:
            result = orch.review(tmp_path, mode="full")

            for required in schema.get("required", []):
                check(f"output has required field '{required}'", required in result)

            artifact_type_enum = schema.get("properties", {}).get("artifact_type", {}).get("enum", [])
            check(f"artifact_type '{result['artifact_type']}' is valid enum",
                   result["artifact_type"] in artifact_type_enum)

            check("confidence_score is number",
                   isinstance(result.get("confidence_score"), (int, float)))
            check("need_review is bool",
                   isinstance(result.get("need_review"), bool))
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    print("\n[10] Full mode — HITL flags for critical content")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Budget Report\n\nDeadline: 2026-07-15\nBudget: $50,000\n")
        tmp_path = f.name

    try:
        result = orch.review(tmp_path, mode="full")
        check("hitl_flags is a list", isinstance(result.get("hitl_flags"), list))
        if result.get("hitl_flags"):
            flag = result["hitl_flags"][0]
            check("hitl_flag has 'item_id'", "item_id" in flag)
            check("hitl_flag has 'question'", "question" in flag)
            check("hitl_flag has 'rationale'", "rationale" in flag)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return _summary("orchestrator", exit_on_fail=True)


if __name__ == "__main__":
    sys.exit(main())
