#!/usr/bin/env python3
"""
schema-validation.test.py — vibe-sop-orchestrator

Validates:
1. All schema/*.schema.json are valid draft-07 schemas.
2. Fixture instances in synthetic-data/ validate against their schema.
3. Invalid fixture instances are correctly rejected.
4. Contract schemas emit evidence/confidence_score/need_review per schema contract.
   Schema list derived dynamically from skill.json — stays in sync automatically.

Fixtures live in synthetic-data/ as JSON files named {artifact}-{variant}.json:
  - {artifact}-valid.json     — full valid instance
  - {artifact}-invalid.json   — malformed instance (missing/wrong fields)
  - {artifact}-minimal.json   — minimal instance for contract test

Run:
    python3 test/schema-validation.test.py
"""

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
    print("SCHEMA VALIDATION TEST \u2014 vibe-sop-orchestrator")
    print("=" * 60)

    SKILL_DIR = get_skill_dir()
    schemas = load_schemas()

    # 1. All schemas parse as valid JSON
    print("\n[1] Schemas parse as valid JSON")
    schema_files = sorted((SKILL_DIR / "schema").glob("*.schema.json"))
    check("found \u22651 schema file", len(schema_files) >= 1, f"found {len(schema_files)}")
    for sf in schema_files:
        print(f"    \u2713 {sf.name}")
        passed += 1

    # 2. deep-analysis-trigger validates a valid document
    print("\n[2] deep-analysis-trigger.schema.json validates valid document")
    trigger_schema = schemas.get("deep-analysis-trigger.schema.json")
    if trigger_schema:
        if fixture_exists("deep-analysis-trigger-valid"):
            valid_doc = load_fixture("deep-analysis-trigger-valid")
            errs = validate(trigger_schema, valid_doc)
            check("valid trigger passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("deep-analysis-trigger-valid.json fixture exists", False)
    else:
        check("deep-analysis-trigger.schema.json exists", False, "schema file not found")

    # 3. deep-analysis-trigger rejects invalid document
    print("\n[3] deep-analysis-trigger.schema.json rejects invalid document")
    if trigger_schema:
        if fixture_exists("deep-analysis-trigger-invalid"):
            invalid_doc = load_fixture("deep-analysis-trigger-invalid")
            errs = validate(trigger_schema, invalid_doc)
            check("invalid trigger rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("deep-analysis-trigger-invalid.json fixture exists", False)
    else:
        check("deep-analysis-trigger.schema.json exists", False, "schema file not found")

    # 4. sop-content validates a valid SOP document
    print("\n[4] sop-content.schema.json validates valid SOP document")
    content_schema = schemas.get("sop-content.schema.json")
    if content_schema:
        if fixture_exists("sop-content-valid"):
            valid_sop = load_fixture("sop-content-valid")
            errs = validate(content_schema, valid_sop)
            check("valid SOP content passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("sop-content-valid.json fixture exists", False)
    else:
        check("sop-content.schema.json exists", False, "schema file not found")

    # 5. sop-content rejects invalid document (missing required fields)
    print("\n[5] sop-content.schema.json rejects invalid document")
    if content_schema:
        if fixture_exists("sop-content-invalid"):
            invalid_sop = load_fixture("sop-content-invalid")
            errs = validate(content_schema, invalid_sop)
            check("invalid SOP rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("sop-content-invalid.json fixture exists", False)
    else:
        check("sop-content.schema.json exists", False, "schema file not found")

    # 6. sop-metadata validates a valid metadata document
    print("\n[6] sop-metadata.schema.json validates valid metadata")
    meta_schema = schemas.get("sop-metadata.schema.json")
    if meta_schema:
        if fixture_exists("sop-metadata-valid"):
            valid_meta = load_fixture("sop-metadata-valid")
            errs = validate(meta_schema, valid_meta)
            check("valid SOP metadata passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("sop-metadata-valid.json fixture exists", False)
    else:
        check("sop-metadata.schema.json exists", False, "schema file not found")

    # 7. sop-metadata rejects invalid metadata
    print("\n[7] sop-metadata.schema.json rejects invalid metadata")
    if meta_schema:
        if fixture_exists("sop-metadata-invalid"):
            invalid_meta = load_fixture("sop-metadata-invalid")
            errs = validate(meta_schema, invalid_meta)
            check("invalid metadata rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("sop-metadata-invalid.json fixture exists", False)
    else:
        check("sop-metadata.schema.json exists", False, "schema file not found")

    # 8. Schema contract: schemas declared in skill.json's emits_evidence_confidence
    #    must expose evidence/confidence_score/need_review.
    #    Derived dynamically so the test stays in sync with skill.json.
    print("\n[8] Schema contract \u2014 schemas declared in skill.json emit evidence/confidence_score/need_review")
    skill_meta = json.loads((SKILL_DIR / "skill.json").read_text())
    contract_artifacts = skill_meta.get("integrations", {}).get("schema_contract", {}).get("emits_evidence_confidence", [])
    check("skill.json lists >=1 artifact in emits_evidence_confidence", len(contract_artifacts) >= 1)
    for artifact in contract_artifacts:
        schema_file = f"{artifact}.schema.json"
        s = schemas.get(schema_file)
        if not s:
            check(f"{artifact}.schema.json found in schema/", False, "schema file missing \u2014 update test or add schema")
            continue
        fixture_name = f"{artifact}-minimal"
        if not fixture_exists(fixture_name):
            check(f"{artifact} has minimal instance fixture", False, f"missing synthetic-data/{fixture_name}.json")
            continue
        doc = load_fixture(fixture_name)
        errs = validate(s, doc)
        check(
            f"{artifact} schema accepts minimal instance with evidence/confidence_score/need_review",
            not errs,
            "; ".join(e.message for e in errs[:3]),
        )

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())