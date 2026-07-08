#!/usr/bin/env python3
"""
integration.test.py — Integration tests: vibe-sop-orchestrator ↔ vibe-company-orchestrator

Tests cross-skill contracts (symlinks, skill.json declarations, schema validation,
evidence contract, error recovery).

Run:
    python3 test/integration.test.py
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "script"))

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


def get_skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def get_company_dir() -> Path:
    return get_skill_dir().parent / "vibe-company-orchestrator"


def main():
    global passed, failed
    SKILL_DIR = get_skill_dir()
    COMPANY_DIR = get_company_dir()

    print("=" * 60)
    print("INTEGRATION TEST \u2014 sop-orchestrator \u2194 company-orchestrator")
    print("=" * 60)

    # ========================================================================
    # SLICE 1: Symlink Integrity
    # ========================================================================
    print("\n[1] Symlink integrity \u2014 scripts symlinked from company-orchestrator")

    check("company-orchestrator script dir exists", COMPANY_DIR.is_dir())

    sop_script_dir = SKILL_DIR / "script"
    company_script_dir = COMPANY_DIR / "script"

    check("sop-orchestrator script dir exists", sop_script_dir.is_dir())
    check("company-orchestrator script dir exists", company_script_dir.is_dir())

    # Expected script files (must match both dirs)
    expected_scripts = {"validator.py", "log_helper.py", "anonymizer.py",
                        "review_queue.py", "install_hooks.sh"}

    sop_scripts = {f.name for f in sop_script_dir.iterdir() if not f.name.startswith(".") and f.name != "__pycache__"}
    company_scripts = {f.name for f in company_script_dir.iterdir() if not f.name.startswith(".")}

    for name in sorted(expected_scripts):
        check(f"expected script '{name}' exists in sop-orchestrator/script/",
              name in sop_scripts)
        check(f"expected script '{name}' exists in company-orchestrator/script/",
              name in company_scripts)

        sop_path = sop_script_dir / name
        company_path = company_script_dir / name

        is_link = os.path.islink(str(sop_path))
        check(f"'{name}' in sop-orchestrator/script/ is a symlink", is_link,
              f"expected symlink, got regular file")

        if is_link:
            resolved = os.path.realpath(str(sop_path))
            expected_target = str(company_path)
            check(f"'{name}' symlink resolves to company-orchestrator/script/{name}",
                  resolved == expected_target,
                  f"resolves to {resolved}, expected {expected_target}")

    # ========================================================================
    # SLICE 2: Mutual Integration Declarations
    # ========================================================================
    print("\n[2] Mutual integration declarations \u2014 skill.json cross-references")

    sop_skill_json = json.loads((SKILL_DIR / "skill.json").read_text())
    company_skill_json = json.loads((COMPANY_DIR / "skill.json").read_text())

    sop_upstream = sop_skill_json.get("integrations", {}).get("upstream", [])
    company_downstream = company_skill_json.get("integrations", {}).get("downstream", [])

    check("sop-orchestrator skill.json parses as valid JSON", isinstance(sop_skill_json, dict))
    check("company-orchestrator skill.json parses as valid JSON", isinstance(company_skill_json, dict))

    check(
        "sop-orchestrator declares 'vibe-company-orchestrator' as upstream",
        "vibe-company-orchestrator" in sop_upstream,
        f"upstream = {sop_upstream}",
    )
    check(
        "company-orchestrator declares 'vibe-sop-orchestrator' as downstream",
        "vibe-sop-orchestrator" in company_downstream,
        f"downstream = {company_downstream}",
    )

    # Guardrails consistency
    sop_guardrails = sop_skill_json.get("guardrails", {})
    company_guardrails = company_skill_json.get("guardrails", {})

    check(
        "both skills require evidence",
        sop_guardrails.get("evidence_required") == True
        and company_guardrails.get("evidence_required") == True,
    )
    check(
        "both skills have confidence_threshold == 0.7",
        sop_guardrails.get("confidence_threshold") == 0.7
        and company_guardrails.get("confidence_threshold") == 0.7,
    )
    check(
        "both skills protect template/ and archive/",
        sop_guardrails.get("hooks_protected_paths") == ["template/", "archive/"]
        and company_guardrails.get("hooks_protected_paths") == ["template/", "archive/"],
    )

    # ========================================================================
    # SLICE 3: Schema Cross-Validation
    # ========================================================================
    print("\n[3] Schema cross-validation \u2014 shared validator.py handles both skills")

    from validator import validate_artifact, validate_instance

    # 3a. Sop-orchestrator: each valid fixture validates against its schema
    print("\n  3a. Sop-orchestrator \u2014 valid fixtures pass schema validation")
    sop_schemas_dir = SKILL_DIR / "schema"
    sop_synthetic_dir = SKILL_DIR / "synthetic-data"

    sop_schema_map = {
        "sop-content-valid": "sop-content.schema.json",
        "sop-content-minimal": "sop-content.schema.json",
        "sop-metadata-valid": "sop-metadata.schema.json",
        "sop-metadata-minimal": "sop-metadata.schema.json",
        "deep-analysis-trigger-valid": "deep-analysis-trigger.schema.json",
        "deep-analysis-trigger-minimal": "deep-analysis-trigger.schema.json",
        "deep-mode-handoff-valid": "xthinking-handoff-brief.schema.json",
        "deep-mode-handoff-minimal": "xthinking-handoff-brief.schema.json",
        "quick-mode-critical-params": "sop-content.schema.json",
    }

    for fixture_name, schema_name in sorted(sop_schema_map.items()):
        fixture_path = sop_synthetic_dir / f"{fixture_name}.json"
        schema_path = sop_schemas_dir / schema_name
        if fixture_path.is_file() and schema_path.is_file():
            result = validate_artifact(str(fixture_path), str(schema_path))
            check(f"sop: {fixture_name}.json vs {schema_name}", result["ok"],
                  "; ".join(result["errors"][:3]))
        else:
            missing = []
            if not fixture_path.is_file():
                missing.append(fixture_name)
            if not schema_path.is_file():
                missing.append(schema_name)
            check(f"sop: {fixture_name}.json vs {schema_name}", False,
                  f"missing: {missing}")

    # 3b. Sop-orchestrator: invalid fixtures are correctly rejected
    print("\n  3b. Sop-orchestrator \u2014 invalid fixtures correctly rejected")
    sop_invalid_map = {
        "sop-content-invalid": "sop-content.schema.json",
        "sop-metadata-invalid": "sop-metadata.schema.json",
        "deep-analysis-trigger-invalid": "deep-analysis-trigger.schema.json",
        "deep-mode-handoff-invalid": "xthinking-handoff-brief.schema.json",
    }

    for fixture_name, schema_name in sorted(sop_invalid_map.items()):
        fixture_path = sop_synthetic_dir / f"{fixture_name}.json"
        schema_path = sop_schemas_dir / schema_name
        if fixture_path.is_file() and schema_path.is_file():
            result = validate_artifact(str(fixture_path), str(schema_path))
            check(f"sop: {fixture_name}.json rejected", not result["ok"],
                  f"expected rejection, got ok=True")
        else:
            missing = []
            if not fixture_path.is_file():
                missing.append(fixture_name)
            if not schema_path.is_file():
                missing.append(schema_name)
            check(f"sop: {fixture_name}.json rejected", False,
                  f"missing: {missing}")

    # 3c. Company-orchestrator: sample artifacts pass schema validation
    print("\n  3c. Company-orchestrator \u2014 sample artifacts pass schema validation")
    company_schemas_dir = COMPANY_DIR / "schema"
    company_synthetic_dir = COMPANY_DIR / "synthetic-data"

    company_schema_map = {
        "sample-company-okr": "company-okr.schema.json",
        "sample-handoff-brief": "aiworkforce-handoff-brief.schema.json",
        "sample-quality-standards": "quality-standards.schema.json",
    }

    for fixture_name, schema_name in sorted(company_schema_map.items()):
        fixture_path = company_synthetic_dir / f"{fixture_name}.json"
        schema_path = company_schemas_dir / schema_name
        if fixture_path.is_file() and schema_path.is_file():
            result = validate_artifact(str(fixture_path), str(schema_path))
            check(f"company: {fixture_name}.json vs {schema_name}", result["ok"],
                  "; ".join(result["errors"][:3]))
        else:
            missing = []
            if not fixture_path.is_file():
                missing.append(fixture_name)
            if not schema_path.is_file():
                missing.append(schema_name)
            check(f"company: {fixture_name}.json vs {schema_name}", False,
                  f"missing: {missing}")

    # 3d. Cross-skill: company-orchestrator's skill-meta schema validates sop-orchestrator's skill.json
    print("\n  3d. Cross-skill validation")
    skill_meta_schema_path = company_schemas_dir / "skill-meta.schema.json"
    if skill_meta_schema_path.is_file():
        meta_schema = json.loads(skill_meta_schema_path.read_text())
        sop_skill = json.loads((SKILL_DIR / "skill.json").read_text())
        errs = validate_instance(sop_skill, meta_schema)
        check("skill-meta.schema.json validates sop skill.json", len(errs) == 0,
              "; ".join(errs[:3]))
        company_skill = json.loads((COMPANY_DIR / "skill.json").read_text())
        errs = validate_instance(company_skill, meta_schema)
        check("skill-meta.schema.json validates company skill.json", len(errs) == 0,
              "; ".join(errs[:3]))
    else:
        check("skill-meta.schema.json exists", False, "missing")

    # ========================================================================
    # SLICE 4: Evidence/Confidence/Need Review Contract
    # ========================================================================
    print("\n[4] Evidence contract \u2014 all fixtures emit evidence/confidence_score/need_review")

    required_fields = {"evidence", "confidence_score", "need_review"}

    # Non-invalid fixtures (valid + minimal) must contain all 3 fields.
    # Invalid fixtures are intentionally malformed — skip them.
    def is_contract_fixture(path: Path) -> bool:
        return "invalid" not in path.stem

    # Sop-orchestrator fixtures
    sop_fixtures = sorted(sop_synthetic_dir.glob("*.json"))
    check(f"sop-orchestrator has \u22651 synthetic-data fixture", len(sop_fixtures) >= 1)

    for fp in sop_fixtures:
        if not is_contract_fixture(fp):
            continue
        name = fp.name.replace(".json", "")
        doc = json.loads(fp.read_text())
        present = {f for f in required_fields if f in doc}
        missing = required_fields - present
        check(
            f"sop: {name} has all 3 required fields",
            len(missing) == 0,
            f"missing: {sorted(missing)}",
        )

    # Company-orchestrator fixtures
    company_fixtures = sorted(company_synthetic_dir.glob("*.json"))
    check(f"company-orchestrator has \u22651 synthetic-data fixture", len(company_fixtures) >= 1)

    for fp in company_fixtures:
        if not is_contract_fixture(fp):
            continue
        name = fp.name.replace(".json", "")
        doc = json.loads(fp.read_text())
        present = {f for f in required_fields if f in doc}
        missing = required_fields - present
        check(
            f"company: {name} has all 3 required fields",
            len(missing) == 0,
            f"missing: {sorted(missing)}",
        )

    # Verify confidence_score values are in [0, 1] range
    print("\n  4a. confidence_score in valid range [0, 1]")
    for fp in sop_fixtures + company_fixtures:
        if not is_contract_fixture(fp):
            continue
        name = f"{fp.parent.parent.name}/{fp.name}"
        doc = json.loads(fp.read_text())
        if "confidence_score" in doc:
            cs = doc["confidence_score"]
            check(
                f"{name} confidence_score={cs} in [0,1]",
                isinstance(cs, (int, float)) and 0 <= cs <= 1,
                f"confidence_score={cs} out of range",
            )

    # Verify need_review is a boolean
    print("\n  4b. need_review is boolean")
    for fp in sop_fixtures + company_fixtures:
        if not is_contract_fixture(fp):
            continue
        name = f"{fp.parent.parent.name}/{fp.name}"
        doc = json.loads(fp.read_text())
        if "need_review" in doc:
            nr = doc["need_review"]
            check(
                f"{name} need_review={nr} is bool",
                isinstance(nr, bool),
                f"need_review={nr} is {type(nr).__name__}",
            )

    # Verify evidence is a list
    print("\n  4c. evidence is a list")
    for fp in sop_fixtures + company_fixtures:
        if not is_contract_fixture(fp):
            continue
        name = f"{fp.parent.parent.name}/{fp.name}"
        doc = json.loads(fp.read_text())
        if "evidence" in doc:
            ev = doc["evidence"]
            check(
                f"{name} evidence is list",
                isinstance(ev, list),
                f"evidence is {type(ev).__name__}",
            )

    # ========================================================================
    # SLICE 5: Error Recovery
    # ========================================================================
    print("\n[5] Error recovery \u2014 validator.py handles malformed input gracefully")

    import tempfile

    # 5a. Non-existent file → graceful error (no crash)
    print("\n  5a. Non-existent paths")
    result = validate_artifact("/tmp/nonexistent-artifact.json",
                               str(sop_schemas_dir / "sop-content.schema.json"))
    check("validate_artifact missing artifact → ok=False", not result["ok"])
    check("validate_artifact missing artifact → descriptive error",
          any("Cannot read" in e for e in result.get("errors", [])),
          f"errors: {result.get('errors')}")

    result = validate_artifact(str(sop_synthetic_dir / "sop-content-valid.json"),
                               "/tmp/nonexistent-schema.json")
    check("validate_artifact missing schema → ok=False", not result["ok"])
    check("validate_artifact missing schema → descriptive error",
          any("Cannot read" in e for e in result.get("errors", [])),
          f"errors: {result.get('errors')}")

    # 5b. Invalid JSON content → graceful error
    print("\n  5b. Invalid JSON content")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        tf.write("this is not json {{{ broken")
        bad_json_path = tf.name
    result = validate_artifact(bad_json_path,
                               str(sop_schemas_dir / "sop-content.schema.json"))
    os.unlink(bad_json_path)
    check("validate_artifact invalid JSON → ok=False", not result["ok"])
    check("validate_artifact invalid JSON → descriptive error",
          any("Cannot read" in e or "JSON" in e for e in result.get("errors", [])),
          f"errors: {result.get('errors')}")

    # 5c. validate_instance — missing required fields → descriptive errors
    print("\n  5c. Missing required fields")
    content_schema = json.loads((sop_schemas_dir / "sop-content.schema.json").read_text())
    errs = validate_instance({"sop_code": "TEST"}, content_schema)
    check("missing fields generates errors", len(errs) > 0)
    has_field_error = any("required" in e.lower() or "missing" in e.lower() for e in errs)
    check("errors mention missing fields", has_field_error,
          f"errors don't mention missing fields: {errs[:3]}")

    # 5d. Wrong types → descriptive errors
    print("\n  5d. Wrong data types")
    wrong_type_doc = {
        "sop_code": 12345,  # should be string
        "title": True,       # should be string
        "process": "not a list",  # should be list
        "evidence": "not a list",
        "confidence_score": "high",  # should be number
        "need_review": "yes",  # should be boolean
    }
    errs = validate_instance(wrong_type_doc, content_schema)
    check("wrong types generates errors", len(errs) > 0)
    has_type_error = any("expected type" in e.lower() for e in errs)
    check("errors mention type mismatches", has_type_error,
          f"errors don't mention types: {errs[:3]}")

    # 5e. Empty document → graceful
    print("\n  5e. Empty/minimal edge cases")
    errs = validate_instance({}, content_schema)
    check("empty dict generates validation errors", len(errs) > 0,
          "empty document should fail with required field errors")

    errs = validate_instance(None, content_schema)
    check("null instance generates errors", len(errs) > 0)

    errs = validate_instance([], content_schema)
    check("array instance (expected object) generates errors", len(errs) > 0)

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
