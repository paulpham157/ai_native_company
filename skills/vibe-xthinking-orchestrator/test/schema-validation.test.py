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
    print("SCHEMA VALIDATION TEST \u2014 vibe-xthinking-orchestrator")
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

    # 2. topic-analysis schema
    print("\n[2] topic-analysis.schema.json")
    topic_schema = schemas.get("topic-analysis.schema.json")
    if topic_schema:
        if fixture_exists("topic-analysis-valid"):
            errs = validate(topic_schema, load_fixture("topic-analysis-valid"))
            check("valid passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("topic-analysis-valid.json fixture exists", False)
        if fixture_exists("topic-analysis-invalid"):
            errs = validate(topic_schema, load_fixture("topic-analysis-invalid"))
            check("invalid rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("topic-analysis-invalid.json fixture exists", False)
    else:
        check("topic-analysis.schema.json exists", False, "schema file not found")

    # 3. problem-analysis schema
    print("\n[3] problem-analysis.schema.json")
    problem_schema = schemas.get("problem-analysis.schema.json")
    if problem_schema:
        if fixture_exists("problem-analysis-valid"):
            errs = validate(problem_schema, load_fixture("problem-analysis-valid"))
            check("valid passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("problem-analysis-valid.json fixture exists", False)
        if fixture_exists("problem-analysis-invalid"):
            errs = validate(problem_schema, load_fixture("problem-analysis-invalid"))
            check("invalid rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("problem-analysis-invalid.json fixture exists", False)
    else:
        check("problem-analysis.schema.json exists", False, "schema file not found")

    # 4. decision-analysis schema
    print("\n[4] decision-analysis.schema.json")
    decision_schema = schemas.get("decision-analysis.schema.json")
    if decision_schema:
        if fixture_exists("decision-analysis-valid"):
            errs = validate(decision_schema, load_fixture("decision-analysis-valid"))
            check("valid passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("decision-analysis-valid.json fixture exists", False)
        if fixture_exists("decision-analysis-invalid"):
            errs = validate(decision_schema, load_fixture("decision-analysis-invalid"))
            check("invalid rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("decision-analysis-invalid.json fixture exists", False)
    else:
        check("decision-analysis.schema.json exists", False, "schema file not found")

    # 5. evidence-tracking schema
    print("\n[5] evidence-tracking.schema.json")
    evidence_schema = schemas.get("evidence-tracking.schema.json")
    if evidence_schema:
        if fixture_exists("evidence-tracking-valid"):
            errs = validate(evidence_schema, load_fixture("evidence-tracking-valid"))
            check("valid passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("evidence-tracking-valid.json fixture exists", False)
        if fixture_exists("evidence-tracking-invalid"):
            errs = validate(evidence_schema, load_fixture("evidence-tracking-invalid"))
            check("invalid rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("evidence-tracking-invalid.json fixture exists", False)
    else:
        check("evidence-tracking.schema.json exists", False, "schema file not found")

    # 6. explicit-thinking schema
    print("\n[6] explicit-thinking.schema.json")
    thinking_schema = schemas.get("explicit-thinking.schema.json")
    if thinking_schema:
        if fixture_exists("explicit-thinking-valid"):
            errs = validate(thinking_schema, load_fixture("explicit-thinking-valid"))
            check("valid passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            check("explicit-thinking-valid.json fixture exists", False)
        if fixture_exists("explicit-thinking-invalid"):
            errs = validate(thinking_schema, load_fixture("explicit-thinking-invalid"))
            check("invalid rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            check("explicit-thinking-invalid.json fixture exists", False)
    else:
        check("explicit-thinking.schema.json exists", False, "schema file not found")

    # 7. Schema contract — evidence/confidence_score/need_review
    print("\n[7] Schema contract \u2014 evidence/confidence_score/need_review")
    skill_meta = json.loads((SKILL_DIR / "skill.json").read_text())
    contract_artifacts = skill_meta.get("integrations", {}).get("schema_contract", {}).get("emits_evidence_confidence", [])
    check("skill.json lists >=1 artifact in emits_evidence_confidence", len(contract_artifacts) >= 1)
    for artifact in contract_artifacts:
        schema_file = f"{artifact}.schema.json"
        s = schemas.get(schema_file)
        if not s:
            check(f"{artifact}.schema.json found in schema/", False, "schema file missing")
            continue
        fixture_name = f"{artifact}-minimal"
        if not fixture_exists(fixture_name):
            check(f"{artifact} has minimal instance fixture", False, f"missing synthetic-data/{fixture_name}.json")
            continue
        doc = load_fixture(fixture_name)
        errs = validate(s, doc)
        check(
            f"{artifact} schema accepts minimal with evidence/confidence_score/need_review",
            not errs,
            "; ".join(e.message for e in errs[:3]),
        )

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())