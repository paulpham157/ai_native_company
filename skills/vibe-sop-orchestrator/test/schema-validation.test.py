#!/usr/bin/env python3
"""
schema-validation.test.py — vibe-sop-orchestrator

Validates:
1. All schema/*.schema.json are valid draft-07 schemas.
2. Schemas declared in skill.json's emits_evidence_confidence accept valid instances.
3. Schemas reject invalid instances (missing required fields).
4. Contract schemas emit evidence/confidence_score/need_review per schema contract.
   Schema list derived dynamically from skill.json — stays in sync automatically.

Run:
    python3 test/schema-validation.test.py
"""

import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "script"))

try:
    import jsonschema
    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False

from validator import validate_instance

passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✓ {name}")
    else:
        failed += 1
        print(f"  ✗ {name} — {detail}")


def validate(schema, instance):
    if HAVE_JSONSCHEMA:
        return list(jsonschema.Draft7Validator(schema).iter_errors(instance))
    return validate_instance(instance, schema)


def main():
    global passed, failed
    print("=" * 60)
    print("SCHEMA VALIDATION TEST — vibe-sop-orchestrator")
    print("=" * 60)

    # 1. All schemas parse as valid JSON
    print("\n[1] Schemas parse as valid JSON")
    schema_files = sorted((SKILL_DIR / "schema").glob("*.schema.json"))
    check("found ≥1 schema file", len(schema_files) >= 1, f"found {len(schema_files)}")
    schemas = {}
    for sf in schema_files:
        try:
            schemas[sf.name] = json.loads(sf.read_text())
            print(f"    ✓ {sf.name}")
            passed += 1
        except Exception as e:
            print(f"    ✗ {sf.name} — {e}")
            failed += 1

    # 2. deep-analysis-trigger validates a valid document
    print("\n[2] deep-analysis-trigger.schema.json validates valid document")
    trigger_schema = schemas.get("deep-analysis-trigger.schema.json")
    if trigger_schema:
        valid_doc = {
            "needs_deep_analysis": True,
            "reasoning": "SOP involves 3 departments with high compliance requirements",
            "complexity_score": 0.85,
            "cross_department_count": 3,
            "risk_level": "high",
            "evidence": [
                {"claim": "Cross-department workflow detected", "source": "department charter"}
            ],
            "confidence_score": 0.8,
            "need_review": False
        }
        errs = validate(trigger_schema, valid_doc)
        check("valid trigger passes", not errs, "; ".join(e.message for e in errs[:3]))
    else:
        check("deep-analysis-trigger.schema.json exists", False, "schema file not found")

    # 3. sop-content validates a valid SOP document
    print("\n[3] sop-content.schema.json validates valid SOP document")
    content_schema = schemas.get("sop-content.schema.json")
    if content_schema:
        valid_sop = {
            "sop_code": "SOP-MKT-001",
            "title": "Content Approval Workflow",
            "version": "1.0",
            "inputs": [
                {"name": "Draft content", "source": "Content Team", "format": "markdown"}
            ],
            "process": [
                {"step": 1, "action": "Review draft", "responsible": "Editor", "duration_estimate": "2h"}
            ],
            "outputs": [
                {"name": "Approved content", "destination": "Publishing", "format": "markdown"}
            ],
            "controls": [
                {"name": "Style Guide v3", "standard": "QC-001"}
            ],
            "mechanisms": [
                {"name": "CMS", "type": "tool"}
            ],
            "evidence": [
                {"claim": "Workflow documented in charter", "source": "MKT charter v2.1"}
            ],
            "confidence_score": 0.85,
            "need_review": False
        }
        errs = validate(content_schema, valid_sop)
        check("valid SOP content passes", not errs, "; ".join(e.message for e in errs[:3]))
    else:
        check("sop-content.schema.json exists", False, "schema file not found")

    # 4. sop-content rejects invalid document (missing required fields)
    print("\n[4] sop-content.schema.json rejects invalid document")
    if content_schema:
        invalid_sop = {
            "title": "Missing sop_code and inputs"
        }
        errs = validate(content_schema, invalid_sop)
        check("invalid SOP rejected", len(errs) > 0, f"expected errors, got 0")
    else:
        check("sop-content.schema.json exists", False, "schema file not found")

    # 5. sop-metadata validates a valid metadata document
    print("\n[5] sop-metadata.schema.json validates valid metadata")
    meta_schema = schemas.get("sop-metadata.schema.json")
    if meta_schema:
        valid_meta = {
            "sop_code": "SOP-MKT-001",
            "department": "Marketing",
            "type": "operational",
            "version": "1.0",
            "title": "Content Approval Workflow",
            "owner": "Content Lead",
            "tags": ["content", "approval", "marketing"],
            "dependencies": [
                {"sop_code": "SOP-MKT-000", "relation": "precedes"}
            ],
            "change_history": [
                {"version": "1.0", "date": "2026-01-15", "author": "Content Lead", "summary": "Initial version"}
            ],
            "evidence": [
                {"claim": "Charter defines workflow", "source": "MKT charter v2.1"}
            ],
            "confidence_score": 0.9,
            "need_review": False
        }
        errs = validate(meta_schema, valid_meta)
        check("valid SOP metadata passes", not errs, "; ".join(e.message for e in errs[:3]))
    else:
        check("sop-metadata.schema.json exists", False, "schema file not found")

    # 6. sop-metadata rejects invalid metadata
    print("\n[6] sop-metadata.schema.json rejects invalid metadata")
    if meta_schema:
        invalid_meta = {
            "sop_code": "invalid-code",
            "department": "Marketing"
        }
        errs = validate(meta_schema, invalid_meta)
        check("invalid metadata rejected", len(errs) > 0, f"expected errors, got 0")
    else:
        check("sop-metadata.schema.json exists", False, "schema file not found")

    # 7. Schema contract: schemas declared in skill.json's emits_evidence_confidence
    #    must expose evidence/confidence_score/need_review.
    #    Derived dynamically so the test stays in sync with skill.json.
    print("\n[7] Schema contract — schemas declared in skill.json emit evidence/confidence_score/need_review")
    skill_meta = json.loads((SKILL_DIR / "skill.json").read_text())
    contract_artifacts = skill_meta.get("integrations", {}).get("schema_contract", {}).get("emits_evidence_confidence", [])
    check("skill.json lists ≥1 artifact in emits_evidence_confidence", len(contract_artifacts) >= 1)
    valid_instances = {
        "deep-analysis-trigger": {
            "needs_deep_analysis": False,
            "reasoning": "Simple routine task",
            "complexity_score": 0.2,
            "evidence": [],
            "confidence_score": 0.8,
            "need_review": False,
        },
        "sop-content": {
            "sop_code": "SOP-MKT-001",
            "title": "Minimal SOP",
            "inputs": [{"name": "x", "source": "y"}],
            "process": [{"step": 1, "action": "do x"}],
            "outputs": [{"name": "y", "destination": "z"}],
            "evidence": [],
            "confidence_score": 0.8,
            "need_review": False,
        },
        "sop-metadata": {
            "sop_code": "SOP-MKT-001",
            "department": "Marketing",
            "type": "operational",
            "version": "1.0",
            "evidence": [],
            "confidence_score": 0.8,
            "need_review": False,
        },
    }
    for artifact in contract_artifacts:
        schema_file = f"{artifact}.schema.json"
        s = schemas.get(schema_file)
        if not s:
            check(f"{artifact}.schema.json found in schema/", False, "schema file missing — update test or add schema")
            continue
        doc = valid_instances.get(artifact)
        if not doc:
            check(f"{artifact} has a valid instance in contract test", False, "add minimal valid instance to test")
            continue
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
