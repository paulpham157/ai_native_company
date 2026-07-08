#!/usr/bin/env python3
"""
schema-validation.test.py — vibe-sop-orchestrator

Validates:
1. All schema/*.schema.json are valid draft-07 schemas.
2. deep-analysis-trigger.schema.json validates correctly.

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
        if HAVE_JSONSCHEMA:
            errs = list(jsonschema.Draft7Validator(trigger_schema).iter_errors(valid_doc))
            check("valid trigger passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            errs = validate_instance(valid_doc, trigger_schema)
            check("valid trigger passes (stdlib)", not errs, "; ".join(errs[:3]))
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
        if HAVE_JSONSCHEMA:
            errs = list(jsonschema.Draft7Validator(content_schema).iter_errors(valid_sop))
            check("valid SOP content passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            errs = validate_instance(valid_sop, content_schema)
            check("valid SOP content passes (stdlib)", not errs, "; ".join(errs[:3]))
    else:
        check("sop-content.schema.json exists", False, "schema file not found")

    # 4. sop-content rejects invalid document (missing required fields)
    print("\n[4] sop-content.schema.json rejects invalid document")
    if content_schema:
        invalid_sop = {
            "title": "Missing sop_code and inputs"
        }
        if HAVE_JSONSCHEMA:
            errs = list(jsonschema.Draft7Validator(content_schema).iter_errors(invalid_sop))
            check("invalid SOP rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            errs = validate_instance(invalid_sop, content_schema)
            check("invalid SOP rejected (stdlib)", len(errs) > 0, f"expected errors, got 0")
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
        if HAVE_JSONSCHEMA:
            errs = list(jsonschema.Draft7Validator(meta_schema).iter_errors(valid_meta))
            check("valid SOP metadata passes", not errs, "; ".join(e.message for e in errs[:3]))
        else:
            errs = validate_instance(valid_meta, meta_schema)
            check("valid SOP metadata passes (stdlib)", not errs, "; ".join(errs[:3]))
    else:
        check("sop-metadata.schema.json exists", False, "schema file not found")

    # 6. sop-metadata rejects invalid metadata
    print("\n[6] sop-metadata.schema.json rejects invalid metadata")
    if meta_schema:
        invalid_meta = {
            "sop_code": "invalid-code",
            "department": "Marketing"
        }
        if HAVE_JSONSCHEMA:
            errs = list(jsonschema.Draft7Validator(meta_schema).iter_errors(invalid_meta))
            check("invalid metadata rejected", len(errs) > 0, f"expected errors, got 0")
        else:
            errs = validate_instance(invalid_meta, meta_schema)
            check("invalid metadata rejected (stdlib)", len(errs) > 0, f"expected errors, got 0")
    else:
        check("sop-metadata.schema.json exists", False, "schema file not found")

    # 7. Schema contract: all schemas emit evidence/confidence_score/need_review
    print("\n[7] Schema contract — all schemas emit evidence, confidence_score, need_review")
    required_fields = {"evidence", "confidence_score", "need_review"}
    sop_schemas = ["deep-analysis-trigger.schema.json", "sop-content.schema.json", "sop-metadata.schema.json"]
    for name in sop_schemas:
        s = schemas.get(name)
        if s:
            props = set(s.get("properties", {}).keys())
            missing = required_fields - props
            check(f"{name} has all contract fields", not missing, f"missing: {missing}")
        else:
            check(f"{name} exists", False, "schema file not found")

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
