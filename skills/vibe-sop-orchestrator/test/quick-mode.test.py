#!/usr/bin/env python3
"""
quick-mode.test.py — Quick mode workflow tests

Tests (behavior, not shape):
1. Template cloning — templates exist and are readable
2. Mode selection rubric scoring — weighted score < 20 → Quick mode
3. Critical parameters blocked — BLOCKED fields not filled by AI
4. Schema validation — Quick mode output passes schema
5. Emit — evidence/confidence_score/need_review present
6. Prompt template — quick-mode-sop.md exists and complete
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "script"))

from test_helpers import (
    get_skill_dir,
    get_synthetic_dir,
    load_fixture,
    fixture_exists,
    load_schemas,
    validate,
)

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
    print("QUICK MODE TEST \u2014 vibe-sop-orchestrator")
    print("=" * 60)

    SKILL_DIR = get_skill_dir()
    synthetic_dir = get_synthetic_dir()

    # 1. Template files exist and are readable
    print("\n[1] Template cloning \u2014 templates exist and are readable")
    template_dir = SKILL_DIR / "kb" / "templates"
    industry_dir = SKILL_DIR / "kb" / "industry-sop-templates"

    expected_templates = {"sop-operational.md", "sop-documentation.md"}
    templates = {t.name for t in template_dir.glob("*.md")}
    for name in sorted(expected_templates):
        check(f"template {name} exists", name in templates)
        check(f"template {name} readable", (template_dir / name).stat().st_size > 0)

    expected_industry = {"tech-startup.md", "consulting.md", "ecommerce.md"}
    industry_templates = {t.name for t in industry_dir.glob("*.md")}
    for name in sorted(expected_industry):
        check(f"industry template {name} exists", name in industry_templates)
        check(f"industry template {name} readable", (industry_dir / name).stat().st_size > 0)

    # 2. Mode selection: weighted score < 20
    print("\n[2] Mode selection rubric \u2014 Quick mode when score < 20")
    rubric_path = SKILL_DIR / "kb" / "mode-selection-rubric.md"
    rubric_text = rubric_path.read_text()
    check("mode-selection-rubric.md exists", rubric_path.is_file())

    rubric_lines = rubric_text.splitlines()
    quick_threshold_lines = [
        line for line in rubric_lines
        if "quick mode" in line.lower()
    ]
    check(
        "rubric mentions Quick mode threshold line with score < 20",
        any(
            "score" in line.lower()
            and "20" in line
            and any(sym in line for sym in ["<", "\u2190", "D\u01b0\u1edbi", "under", "below"])
            for line in quick_threshold_lines
        ),
        "Expected a line like 'Quick mode when weighted score < 20' or 'D\u01b0\u1edbi 20 \u2192 Quick mode'"
    )

    override_lines = [
        line for line in rubric_lines
        if "override" in line.lower()
    ]
    check(
        "user override for Quick mode mentioned",
        len(override_lines) > 0,
        "Expected rubric to mention how users override Quick mode"
    )

    # 3. Critical parameters must NOT be auto-filled by AI
    print("\n[3] Critical parameters \u2014 AI must NOT auto-fill")
    skill_text = (SKILL_DIR / "SKILL.md").read_text()
    critical_keywords = ["deadlines", "SLAs", "KPI targets", "DO_USER_SPECIFY"]
    for kw in critical_keywords:
        check(
            f"SKILL.md mentions '{kw}' as blocked",
            kw.lower() in skill_text.lower(),
            f"'{kw}' not found in SKILL.md",
        )

    quick_prompt_path = SKILL_DIR / "prompt" / "quick-mode-sop.md"
    check("quick-mode prompt template exists", quick_prompt_path.is_file())
    check(
        "prompt template mentions BLOCKED fields",
        "[DO_USER_SPECIFY]" in quick_prompt_path.read_text(),
        "Quick-mode prompt template does not reference [DO_USER_SPECIFY]",
    )

    # Behavioral guard: a minimal Quick mode output fixture must NOT concretely
    # fill critical parameters (deadlines / SLAs / KPI targets)
    quick_fixture = synthetic_dir / "quick-mode-critical-params.json"
    check(
        "quick-mode critical-params fixture exists",
        quick_fixture.is_file(),
        f"Missing Quick mode critical-params fixture at {quick_fixture}",
    )

    fixture_data = json.loads(quick_fixture.read_text())
    serialized = json.dumps(fixture_data, indent=2, sort_keys=True)

    check(
        "quick-mode fixture includes at least one [DO_USER_SPECIFY] placeholder",
        "[DO_USER_SPECIFY]" in serialized,
        "No DO_USER_SPECIFY placeholder found in quick-mode critical-params fixture",
    )

    blocked_labels = ["deadline", "deadlines", "sla", "slas", "kpi", "kpis"]
    lines = serialized.splitlines()
    found_blocked_filled = False
    for line in lines:
        lowered = line.lower()
        if any(label in lowered for label in blocked_labels):
            if "[do_user_specify]" not in lowered:
                found_blocked_filled = True
                check(
                    "blocked critical parameter remains unfilled in quick-mode fixture",
                    False,
                    f"Blocked critical parameter appears concretely filled: {line.strip()}",
                )
    if not found_blocked_filled:
        check("all blocked critical parameters use [DO_USER_SPECIFY]", True)

    # 4. Schema validation — Quick mode output passes schema
    print("\n[4] Schema validation \u2014 Quick mode output passes schema")
    schemas = load_schemas()
    content_schema = schemas.get("sop-content.schema.json")
    meta_schema = schemas.get("sop-metadata.schema.json")

    if content_schema and fixture_exists("sop-content-valid"):
        sop = load_fixture("sop-content-valid")
        errs = validate(content_schema, sop)
        check("Quick mode SOP content passes schema", not errs,
              "; ".join(e.message for e in errs[:3]))
    else:
        check("sop-content-valid.json fixture exists", False)

    if meta_schema and fixture_exists("sop-metadata-valid"):
        meta = load_fixture("sop-metadata-valid")
        errs = validate(meta_schema, meta)
        check("Quick mode SOP metadata passes schema", not errs,
              "; ".join(e.message for e in errs[:3]))
    else:
        check("sop-metadata-valid.json fixture exists", False)

    # 5. Emit — evidence/confidence_score/need_review present
    print("\n[5] Emit \u2014 evidence/confidence_score/need_review present")
    if fixture_exists("sop-content-valid"):
        sop = load_fixture("sop-content-valid")
        check("sop-content has evidence", "evidence" in sop)
        check("sop-content has confidence_score", "confidence_score" in sop)
        check("sop-content has need_review", "need_review" in sop)
    else:
        check("sop-content-valid.json fixture exists", False)

    if fixture_exists("sop-metadata-valid"):
        meta = load_fixture("sop-metadata-valid")
        check("sop-metadata has evidence", "evidence" in meta)
        check("sop-metadata has confidence_score", "confidence_score" in meta)
        check("sop-metadata has need_review", "need_review" in meta)
    else:
        check("sop-metadata-valid.json fixture exists", False)

    # 6. Prompt file exists
    print("\n[6] Prompt template \u2014 quick-mode-sop.md exists")
    check("prompt/quick-mode-sop.md exists", quick_prompt_path.is_file())
    prompt_text = quick_prompt_path.read_text()
    check("prompt mentions BLOCKED fields", "[DO_USER_SPECIFY]" in prompt_text)
    check("prompt mentions User Review", "User Review" in prompt_text)
    check("prompt mentions Validation", "Validation" in prompt_text)

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())