#!/usr/bin/env python3

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "script"))

from test_helpers import (
    get_skill_dir,
    load_fixture,
    fixture_exists,
    load_schemas,
    validate,
    check,
    summary as _summary,
    passed,
    failed,
)


def main():
    global passed, failed
    print("=" * 60)
    print("SCHEMA VALIDATION TEST \u2014 vibe-review")
    print("=" * 60)

    SKILL_DIR = get_skill_dir()

    # 1. All schemas parse as valid JSON
    print("\n[1] Schemas parse as valid JSON")
    schema_files = sorted((SKILL_DIR / "schema").glob("*.schema.json"))
    check("found \u22651 schema file", len(schema_files) >= 1, f"found {len(schema_files)}")
    for sf in schema_files:
        try:
            json.loads(sf.read_text())
            print(f"    \u2713 {sf.name}")
            passed += 1
        except json.JSONDecodeError as e:
            print(f"    \u2717 {sf.name} \u2014 {e}")
            failed += 1

    schemas = load_schemas()

    # 2. review-result schema
    print("\n[2] review-result.schema.json")
    result_schema = schemas.get("review-result.schema.json")
    if result_schema:
        if fixture_exists("review-result-valid"):
            errs = validate(result_schema, load_fixture("review-result-valid"))
            check("valid passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("review-result-valid.json fixture exists", False)
        if fixture_exists("review-result-invalid"):
            errs = validate(result_schema, load_fixture("review-result-invalid"))
            check("invalid rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("review-result-invalid.json fixture exists", False)
    else:
        check("review-result.schema.json exists", False, "schema file not found")

    # 3. quality-rubric schema
    print("\n[3] quality-rubric.schema.json")
    rubric_schema = schemas.get("quality-rubric.schema.json")
    if rubric_schema:
        if fixture_exists("quality-rubric-valid"):
            errs = validate(rubric_schema, load_fixture("quality-rubric-valid"))
            check("valid passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("quality-rubric-valid.json fixture exists", False)
        if fixture_exists("quality-rubric-invalid"):
            errs = validate(rubric_schema, load_fixture("quality-rubric-invalid"))
            check("invalid rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("quality-rubric-invalid.json fixture exists", False)
    else:
        check("quality-rubric.schema.json exists", False, "schema file not found")

    # 4. review-rules schema
    print("\n[4] review-rules.schema.json")
    rules_schema = schemas.get("review-rules.schema.json")
    if rules_schema:
        if fixture_exists("review-rules-valid"):
            errs = validate(rules_schema, load_fixture("review-rules-valid"))
            check("valid passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("review-rules-valid.json fixture exists", False)
        if fixture_exists("review-rules-invalid"):
            errs = validate(rules_schema, load_fixture("review-rules-invalid"))
            check("invalid rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("review-rules-invalid.json fixture exists", False)
    else:
        check("review-rules.schema.json exists", False, "schema file not found")

    # 5. hitl-checklist schema
    print("\n[5] hitl-checklist.schema.json")
    hitl_schema = schemas.get("hitl-checklist.schema.json")
    if hitl_schema:
        if fixture_exists("hitl-checklist-valid"):
            errs = validate(hitl_schema, load_fixture("hitl-checklist-valid"))
            check("valid passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("hitl-checklist-valid.json fixture exists", False)
        if fixture_exists("hitl-checklist-invalid"):
            errs = validate(hitl_schema, load_fixture("hitl-checklist-invalid"))
            check("invalid rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("hitl-checklist-invalid.json fixture exists", False)
    else:
        check("hitl-checklist.schema.json exists", False, "schema file not found")

    # 6. artifact-type-map schema
    print("\n[6] artifact-type-map.schema.json")
    type_map_schema = schemas.get("artifact-type-map.schema.json")
    if type_map_schema:
        if fixture_exists("artifact-type-map-valid"):
            errs = validate(type_map_schema, load_fixture("artifact-type-map-valid"))
            check("valid passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("artifact-type-map-valid.json fixture exists", False)
        if fixture_exists("artifact-type-map-invalid"):
            errs = validate(type_map_schema, load_fixture("artifact-type-map-invalid"))
            check("invalid rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("artifact-type-map-invalid.json fixture exists", False)
    else:
        check("artifact-type-map.schema.json exists", False, "schema file not found")

    # 7. skill-meta schema is symlinked from company-orchestrator
    print("\n[7] skill-meta.schema.json \u2014 symlinked from company-orchestrator")
    skill_meta_path = SKILL_DIR / "schema" / "skill-meta.schema.json"
    check("skill-meta.schema.json exists", skill_meta_path.exists())
    import os
    check("skill-meta.schema.json is a symlink", os.path.islink(str(skill_meta_path)))

    # 8. Schema contract — evidence/confidence_score/need_review
    print("\n[8] Schema contract \u2014 evidence/confidence_score/need_review")
    result_schema = schemas.get("review-result.schema.json")
    if result_schema:
        result_required = set(result_schema.get("required", []))
        has_evidence = "evidence" in result_required
        has_confidence = "confidence_score" in result_required
        has_review = "need_review" in result_required
        check("review-result requires 'evidence'", has_evidence)
        check("review-result requires 'confidence_score'", has_confidence)
        check("review-result requires 'need_review'", has_review)
    else:
        check("review-result.schema.json exists for contract check", False)

    return _summary("vibe-review schema validation", exit_on_fail=True)


if __name__ == "__main__":
    sys.exit(main())
