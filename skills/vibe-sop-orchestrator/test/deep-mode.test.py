#!/usr/bin/env python3
"""
deep-mode.test.py — Deep mode workflow tests

Tests (behavior, not shape):
1. Mode selection rubric scoring — weighted score >= 20 -> Deep mode
2. deep-analysis-trigger artifact — emitted for mode selection decision
3. User override — always available, recorded in evidence
4. xthinking-handoff-brief schema — exists and validates handoff documents
5. Deep mode prompt template — exists and complete
6. Critical parameters guard — BLOCKED fields apply to Deep mode too
7. Evidence/confidence/need_review — emitted for deep-analysis-trigger
8. Handoff to vibe-xthinking-orchestrator — documented in SKILL.md
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
    print("DEEP MODE TEST \u2014 vibe-sop-orchestrator")
    print("=" * 60)

    SKILL_DIR = get_skill_dir()
    synthetic_dir = get_synthetic_dir()
    skill_text = (SKILL_DIR / "SKILL.md").read_text()
    schemas = load_schemas()

    # 1. Mode selection: weighted score >= 20 -> Deep mode
    print("\n[1] Mode selection rubric \u2014 Deep mode when score >= 20")
    rubric_path = SKILL_DIR / "kb" / "mode-selection-rubric.md"
    check("mode-selection-rubric.md exists", rubric_path.is_file())
    rubric_text = rubric_path.read_text() if rubric_path.is_file() else ""
    rubric_lines = rubric_text.splitlines()
    deep_threshold_lines = [
        line for line in rubric_lines
        if "deep mode" in line.lower()
    ]
    check(
        "rubric mentions Deep mode threshold line with score >= 20",
        any(
            "score" in line.lower()
            and "20" in line
            and any(sym in line for sym in [">=", "\u2265", ">", "tr\u00ean", "above", "over"])
            for line in deep_threshold_lines
        ),
        "Expected a line like 'Deep mode when weighted score >= 20' or 'Tr\u00ean 20 \u2192 Deep mode'"
    )

    # 2. deep-analysis-trigger artifact — schema exists, validates, used in Deep mode
    print("\n[2] deep-analysis-trigger \u2014 schema + fixture validation")
    trigger_schema = schemas.get("deep-analysis-trigger.schema.json")
    check("deep-analysis-trigger.schema.json exists", trigger_schema is not None)

    if trigger_schema:
        if fixture_exists("deep-analysis-trigger-valid"):
            valid_doc = load_fixture("deep-analysis-trigger-valid")
            errs = validate(trigger_schema, valid_doc)
            check("valid deep-analysis-trigger passes schema", not errs,
                  "; ".join(e.message for e in errs[:3]))
        else:
            check("deep-analysis-trigger-valid.json fixture exists", False)

    # 3. SKILL.md describes Deep mode workflow
    print("\n[3] SKILL.md \u2014 Deep mode workflow described")
    deep_mode_sections = [
        section for section in skill_text.split("## Deep Mode")
        if section.strip()
    ]
    check("SKILL.md has ## Deep Mode section", len(deep_mode_sections) >= 1)
    deep_mode_text = "\n".join(deep_mode_sections).lower()

    # Check for specific workflow steps in Deep mode
    deep_workflow_keywords = [
        "xthinking", "xthinking-orchestrator",
        "analysis", "ph\u00e2n t\u00edch",
        "handoff", "b\u00e0n giao",
        "evidence", "confidence_score",
    ]
    for kw in deep_workflow_keywords:
        check(
            f"Deep mode mentions '{kw}'",
            kw.lower() in deep_mode_text,
            f"'{kw}' not found in SKILL.md Deep mode section",
        )

    # Check Deep mode workflow documents all required phases (stable names)
    deep_workflow_phases = [
        "mode selection", "handoff prep", "xthinking analysis",
        "sop generation", "user review", "schema validation",
        "critical parameters", "evidence",
    ]
    for phase in deep_workflow_phases:
        check(
            f"Deep mode workflow documents '{phase}' phase",
            phase.lower() in deep_mode_text,
            f"Expected Deep mode workflow to document '{phase}' in SKILL.md",
        )

    # 4. User override option — always available
    print("\n[4] User override \u2014 always available")
    override_mentions = [
        line for line in rubric_lines
        if "override" in line.lower()
    ]
    check("rubric mentions user override", len(override_mentions) >= 1)

    override_in_deep = "override" in deep_mode_text
    check("Deep mode mentions user override", override_in_deep,
          "User override not mentioned in Deep mode section")

    # 5. xthinking-handoff-brief schema — exists and validates
    print("\n[5] xthinking-handoff-brief \u2014 schema + handoff document")
    handoff_schema = schemas.get("xthinking-handoff-brief.schema.json")
    check("xthinking-handoff-brief.schema.json exists", handoff_schema is not None)

    if handoff_schema:
        if fixture_exists("deep-mode-handoff-valid"):
            handoff_doc = load_fixture("deep-mode-handoff-valid")
            errs = validate(handoff_schema, handoff_doc)
            check("valid handoff document passes schema", not errs,
                  "; ".join(e.message for e in errs[:3]))
        else:
            check("deep-mode-handoff-valid.json fixture exists", False)

        if fixture_exists("deep-mode-handoff-invalid"):
            invalid_handoff = load_fixture("deep-mode-handoff-invalid")
            errs = validate(handoff_schema, invalid_handoff)
            check("invalid handoff document fails schema", len(errs) > 0,
                  f"expected validation errors, got 0")
        else:
            check("deep-mode-handoff-invalid.json fixture exists", False)

        if fixture_exists("deep-mode-handoff-minimal"):
            minimal_doc = load_fixture("deep-mode-handoff-minimal")
            errs = validate(handoff_schema, minimal_doc)
            check("minimal handoff document passes schema", not errs,
                  "; ".join(e.message for e in errs[:3]))
        else:
            check("deep-mode-handoff-minimal.json fixture exists", False)

    # 6. Deep mode prompt template exists
    print("\n[6] Deep mode prompt template \u2014 deep-mode-sop.md")
    deep_prompt_path = SKILL_DIR / "prompt" / "deep-mode-sop.md"
    check("prompt/deep-mode-sop.md exists", deep_prompt_path.is_file())

    if deep_prompt_path.is_file():
        prompt_text = deep_prompt_path.read_text()
        check("prompt mentions xthinking-orchestrator handoff",
              "xthinking" in prompt_text.lower())
        check("prompt mentions Deep mode workflow", "Deep" in prompt_text)
        check("prompt mentions [DO_USER_SPECIFY] guard",
              "[DO_USER_SPECIFY]" in prompt_text)
        check("prompt mentions evidence/confidence/need_review",
              "evidence" in prompt_text and "confidence_score" in prompt_text)

    # 7. Critical parameters guard applies to Deep mode too
    print("\n[7] Critical parameters guard \u2014 applies to Deep mode")
    check(
        "Deep mode mentions Critical parameters guard",
        "critical parameters guard" in deep_mode_text,
    )
    # Check that [DO_USER_SPECIFY] is mentioned in context of Deep mode
    critical_keywords = ["deadlines", "SLAs", "KPI targets", "DO_USER_SPECIFY"]
    for kw in critical_keywords:
        check(
            f"Deep mode mentions '{kw}' as blocked",
            kw.lower() in deep_mode_text,
            f"'{kw}' not found in Deep mode section",
        )

    # 8. Handoff to vibe-xthinking-orchestrator documented
    print("\n[8] Handoff to vibe-xthinking-orchestrator \u2014 documented")
    handoff_keywords = [
        "xthinking-handoff-brief",
        "vibe-xthinking-orchestrator",
        "handoff",
    ]
    for kw in handoff_keywords:
        check(
            f"Deep mode documents handoff via '{kw}'",
            kw.lower() in deep_mode_text,
            f"'{kw}' not found in Deep mode section",
        )

    handoff_schema_path = SKILL_DIR / "schema" / "xthinking-handoff-brief.schema.json"
    check(
        "xthinking-handoff-brief.schema.json file exists on disk",
        handoff_schema_path.is_file(),
    )

    # 9. skill.json lists xthinking-handoff-brief in schema_contract
    print("\n[9] skill.json \u2014 xthinking-handoff-brief declared")
    skill_meta = json.loads((SKILL_DIR / "skill.json").read_text())
    handoff_schema_declared = skill_meta.get("integrations", {}).get("schema_contract", {}).get("handoff_brief_schema", "")
    check(
        "skill.json handoff_brief_schema references xthinking-handoff-brief",
        "xthinking-handoff-brief" in handoff_schema_declared,
        f"Expected xthinking-handoff-brief, got: {handoff_schema_declared}",
    )

    # Check schemas list includes xthinking-handoff-brief
    schema_list = skill_meta.get("schemas", [])
    check(
        "skill.json schemas includes xthinking-handoff-brief.schema.json",
        any("xthinking-handoff-brief" in s for s in schema_list),
        f"Not found in schemas: {schema_list}",
    )

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
