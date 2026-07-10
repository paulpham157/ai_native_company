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


# ============================================================================
# Config — centralised paths, filenames, and mappings
# ============================================================================
EXPECTED_SCRIPTS = {"validator.py", "log_helper.py", "anonymizer.py",
                    "review_queue.py", "install_hooks.sh"}

SOP_SCHEMA_MAP = {
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

SOP_INVALID_MAP = {
    "sop-content-invalid": "sop-content.schema.json",
    "sop-metadata-invalid": "sop-metadata.schema.json",
    "deep-analysis-trigger-invalid": "deep-analysis-trigger.schema.json",
    "deep-mode-handoff-invalid": "xthinking-handoff-brief.schema.json",
}

COMPANY_SCHEMA_MAP = {
    "sample-company-okr": "company-okr.schema.json",
    "sample-handoff-brief": "aiworkforce-handoff-brief.schema.json",
    "sample-quality-standards": "quality-standards.schema.json",
}

EVIDENCE_FIELDS = {"evidence", "confidence_score", "need_review"}


# ============================================================================
# Test runner — encapsulates state so checks are composable without globals
# ============================================================================
class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def check(self, name, condition, detail=""):
        if condition:
            self.passed += 1
            print(f"  \u2713 {name}")
        else:
            self.failed += 1
            print(f"  \u2717 {name} \u2014 {detail}")

    def summary(self):
        print("\n" + "=" * 60)
        print(f"Result: {self.passed} passed, {self.failed} failed")
        print("=" * 60)
        return 0 if self.failed == 0 else 1


# ============================================================================
# Path helpers
# ============================================================================
def get_skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def get_company_dir() -> Path:
    return get_skill_dir().parent / "vibe-company-orchestrator"


def get_xthinking_dir() -> Path:
    return get_skill_dir().parent / "vibe-xthinking-orchestrator"


# ============================================================================
# Fixture-coverage guard: every fixture must be mapped or explicitly excluded.
# Fixtures prefixed with "_" or whose stem contains "-ignore" are excluded.
# ============================================================================
def check_fixture_coverage(runner, synthetic_dir, schema_map, invalid_map, label):
    all_fixtures = list(synthetic_dir.glob("*.json"))
    runner.check(f"{label}: \u22651 synthetic-data fixture", len(all_fixtures) >= 1)

    excluded_stems = {
        p.stem for p in all_fixtures
        if p.name.startswith("_") or "-ignore" in p.stem
    }
    all_stems = {p.stem for p in all_fixtures}
    mapped_stems = set(schema_map.keys()) | set(invalid_map.keys())
    unmapped = sorted(all_stems - mapped_stems - excluded_stems)
    runner.check(
        f"{label}: all fixtures mapped or excluded",
        len(unmapped) == 0,
        f"unmapped fixtures: {unmapped} — add to schema_map or prefix with '_'",
    )


# ============================================================================
# Main
# ============================================================================
def main():
    runner = TestRunner()
    SKILL_DIR = get_skill_dir()
    COMPANY_DIR = get_company_dir()

    print("=" * 60)
    print("INTEGRATION TEST \u2014 sop-orchestrator \u2194 company-orchestrator")
    print("=" * 60)

    # ========================================================================
    # SLICE 1: Symlink Integrity
    # ========================================================================
    print("\n[1] Symlink integrity \u2014 scripts symlinked from company-orchestrator")

    runner.check("company-orchestrator dir exists", COMPANY_DIR.is_dir())

    sop_script_dir = SKILL_DIR / "script"
    company_script_dir = COMPANY_DIR / "script"

    runner.check("sop-orchestrator script dir exists", sop_script_dir.is_dir())
    runner.check("company-orchestrator script dir exists", company_script_dir.is_dir())

    sop_files = {f for f in sop_script_dir.iterdir()
                 if not f.name.startswith(".") and f.name != "__pycache__"}
    sop_script_names = {f.name for f in sop_files}
    company_script_names = {f.name for f in company_script_dir.iterdir()
                            if not f.name.startswith(".")}

    # Every expected script must exist in both dirs and be a symlink in sop
    for name in sorted(EXPECTED_SCRIPTS):
        runner.check(f"expected script '{name}' exists in sop-orchestrator/script/",
                     name in sop_script_names)
        runner.check(f"expected script '{name}' exists in company-orchestrator/script/",
                     name in company_script_names)

        sop_path = sop_script_dir / name
        company_path = company_script_dir / name

        is_link = os.path.islink(str(sop_path))
        runner.check(f"'{name}' in sop-orchestrator/script/ is a symlink", is_link,
                     f"expected symlink, got regular file")

        if is_link:
            resolved = os.path.realpath(str(sop_path))
            expected_target = os.path.realpath(str(company_path))
            runner.check(f"'{name}' symlink resolves to company-orchestrator/script/{name}",
                         resolved == expected_target,
                         f"resolves to {resolved}, expected {expected_target}")

    # Guard: every file in sop/script/ must be an expected script AND a symlink
    unexpected = sop_script_names - EXPECTED_SCRIPTS
    runner.check(
        "no unexpected scripts in sop-orchestrator/script/",
        len(unexpected) == 0,
        f"unexpected file(s): {sorted(unexpected)}",
    )

    for sf in sop_files:
        if sf.name in EXPECTED_SCRIPTS:
            runner.check(
                f"'{sf.name}' is a symlink (no regular files)",
                os.path.islink(str(sf)),
                f"expected symlink, got regular file",
            )

    # ========================================================================
    # SLICE 2: Mutual Integration Declarations
    # ========================================================================
    print("\n[2] Mutual integration declarations \u2014 skill.json cross-references")

    sop_skill_json = json.loads((SKILL_DIR / "skill.json").read_text())
    company_skill_json = json.loads((COMPANY_DIR / "skill.json").read_text())

    sop_upstream = sop_skill_json.get("integrations", {}).get("upstream", [])
    company_downstream = company_skill_json.get("integrations", {}).get("downstream", [])

    runner.check("sop-orchestrator skill.json parses as valid JSON",
                 isinstance(sop_skill_json, dict))
    runner.check("company-orchestrator skill.json parses as valid JSON",
                 isinstance(company_skill_json, dict))

    runner.check(
        "sop-orchestrator declares 'vibe-company-orchestrator' as upstream",
        "vibe-company-orchestrator" in sop_upstream,
        f"upstream = {sop_upstream}",
    )
    runner.check(
        "company-orchestrator declares 'vibe-sop-orchestrator' as downstream",
        "vibe-sop-orchestrator" in company_downstream,
        f"downstream = {company_downstream}",
    )

    sop_guardrails = sop_skill_json.get("guardrails", {})
    company_guardrails = company_skill_json.get("guardrails", {})

    runner.check(
        "both skills require evidence",
        sop_guardrails.get("evidence_required") is True
        and company_guardrails.get("evidence_required") is True,
    )
    runner.check(
        "both skills have confidence_threshold == 0.7",
        sop_guardrails.get("confidence_threshold") == 0.7
        and company_guardrails.get("confidence_threshold") == 0.7,
    )
    runner.check(
        "both skills protect template/ and archive/",
        sop_guardrails.get("hooks_protected_paths") == ["template/", "archive/"]
        and company_guardrails.get("hooks_protected_paths") == ["template/", "archive/"],
    )

    # ========================================================================
    # SLICE 3: Schema Cross-Validation
    # ========================================================================
    print("\n[3] Schema cross-validation \u2014 shared validator.py handles both skills")

    from validator import validate_artifact, validate_instance

    sop_schemas_dir = SKILL_DIR / "schema"
    sop_synthetic_dir = SKILL_DIR / "synthetic-data"

    # Meta-test: every fixture is mapped or explicitly excluded
    print("\n  3a. Fixture-coverage guard")
    check_fixture_coverage(runner, sop_synthetic_dir, SOP_SCHEMA_MAP,
                           SOP_INVALID_MAP, "sop")

    company_schemas_dir = COMPANY_DIR / "schema"
    company_synthetic_dir = COMPANY_DIR / "synthetic-data"

    check_fixture_coverage(runner, company_synthetic_dir, COMPANY_SCHEMA_MAP,
                           {}, "company")

    # 3b. Sop-orchestrator: valid fixtures pass
    print("\n  3b. Sop-orchestrator \u2014 valid fixtures pass schema validation")
    for fixture_name, schema_name in sorted(SOP_SCHEMA_MAP.items()):
        fixture_path = sop_synthetic_dir / f"{fixture_name}.json"
        schema_path = sop_schemas_dir / schema_name
        if fixture_path.is_file() and schema_path.is_file():
            result = validate_artifact(str(fixture_path), str(schema_path))
            runner.check(f"sop: {fixture_name}.json vs {schema_name}", result["ok"],
                         "; ".join(result["errors"][:3]))
        else:
            missing = [p for p, ok in [(fixture_name, fixture_path.is_file()),
                                       (schema_name, schema_path.is_file())] if not ok]
            runner.check(f"sop: {fixture_name}.json vs {schema_name}", False,
                         f"missing: {missing}")

    # 3c. Sop-orchestrator: invalid fixtures are correctly rejected
    print("\n  3c. Sop-orchestrator \u2014 invalid fixtures correctly rejected")
    for fixture_name, schema_name in sorted(SOP_INVALID_MAP.items()):
        fixture_path = sop_synthetic_dir / f"{fixture_name}.json"
        schema_path = sop_schemas_dir / schema_name
        if fixture_path.is_file() and schema_path.is_file():
            result = validate_artifact(str(fixture_path), str(schema_path))
            runner.check(f"sop: {fixture_name}.json rejected", not result["ok"],
                         f"expected rejection, got ok=True")
        else:
            missing = [p for p, ok in [(fixture_name, fixture_path.is_file()),
                                       (schema_name, schema_path.is_file())] if not ok]
            runner.check(f"sop: {fixture_name}.json rejected", False,
                         f"missing: {missing}")

    # 3d. Company-orchestrator: sample artifacts pass
    print("\n  3d. Company-orchestrator \u2014 sample artifacts pass schema validation")
    for fixture_name, schema_name in sorted(COMPANY_SCHEMA_MAP.items()):
        fixture_path = company_synthetic_dir / f"{fixture_name}.json"
        schema_path = company_schemas_dir / schema_name
        if fixture_path.is_file() and schema_path.is_file():
            result = validate_artifact(str(fixture_path), str(schema_path))
            runner.check(f"company: {fixture_name}.json vs {schema_name}", result["ok"],
                         "; ".join(result["errors"][:3]))
        else:
            missing = [p for p, ok in [(fixture_name, fixture_path.is_file()),
                                       (schema_name, schema_path.is_file())] if not ok]
            runner.check(f"company: {fixture_name}.json vs {schema_name}", False,
                         f"missing: {missing}")

    # 3e. Cross-skill: skill-meta validates both skill.json files
    print("\n  3e. Cross-skill validation")
    skill_meta_schema_path = company_schemas_dir / "skill-meta.schema.json"
    if skill_meta_schema_path.is_file():
        meta_schema = json.loads(skill_meta_schema_path.read_text())
        sop_skill = json.loads((SKILL_DIR / "skill.json").read_text())
        errs = validate_instance(sop_skill, meta_schema)
        runner.check("skill-meta.schema.json validates sop skill.json",
                     len(errs) == 0, "; ".join(errs[:3]))
        company_skill = json.loads((COMPANY_DIR / "skill.json").read_text())
        errs = validate_instance(company_skill, meta_schema)
        runner.check("skill-meta.schema.json validates company skill.json",
                     len(errs) == 0, "; ".join(errs[:3]))
    else:
        runner.check("skill-meta.schema.json exists", False, "missing")

    # ========================================================================
    # SLICE 4: Evidence/Confidence/Need Review Contract
    # ========================================================================
    print("\n[4] Evidence contract \u2014 all valid/minimal fixtures emit "
          "evidence/confidence_score/need_review")

    def is_contract_fixture(path: Path) -> bool:
        return "invalid" not in path.stem and "-ignore" not in path.stem

    def check_evidence_contract(fixtures, label):
        for fp in fixtures:
            if not is_contract_fixture(fp):
                continue
            name = fp.name.replace(".json", "")
            doc = json.loads(fp.read_text())
            present = {f for f in EVIDENCE_FIELDS if f in doc}
            missing = EVIDENCE_FIELDS - present
            runner.check(
                f"{label}: {name} has all 3 required fields",
                len(missing) == 0,
                f"missing: {sorted(missing)}",
            )

    sop_fixtures = sorted(sop_synthetic_dir.glob("*.json"))
    check_evidence_contract(sop_fixtures, "sop")

    company_fixtures = sorted(company_synthetic_dir.glob("*.json"))
    check_evidence_contract(company_fixtures, "company")

    # Type/range checks
    print("\n  4a. confidence_score in [0, 1]")
    for fp in sop_fixtures + company_fixtures:
        if not is_contract_fixture(fp):
            continue
        name = f"{fp.parent.parent.name}/{fp.name}"
        doc = json.loads(fp.read_text())
        if "confidence_score" in doc:
            cs = doc["confidence_score"]
            runner.check(
                f"{name} confidence_score={cs} in [0,1]",
                isinstance(cs, (int, float)) and 0 <= cs <= 1,
                f"confidence_score={cs} out of range",
            )

    print("\n  4b. need_review is boolean")
    for fp in sop_fixtures + company_fixtures:
        if not is_contract_fixture(fp):
            continue
        name = f"{fp.parent.parent.name}/{fp.name}"
        doc = json.loads(fp.read_text())
        if "need_review" in doc:
            nr = doc["need_review"]
            runner.check(
                f"{name} need_review={nr} is bool",
                isinstance(nr, bool),
                f"need_review={nr} is {type(nr).__name__}",
            )

    print("\n  4c. evidence is a list")
    for fp in sop_fixtures + company_fixtures:
        if not is_contract_fixture(fp):
            continue
        name = f"{fp.parent.parent.name}/{fp.name}"
        doc = json.loads(fp.read_text())
        if "evidence" in doc:
            ev = doc["evidence"]
            runner.check(
                f"{name} evidence is list",
                isinstance(ev, list),
                f"evidence is {type(ev).__name__}",
            )

    # ========================================================================
    # SLICE 5: Error Recovery
    # ========================================================================
    print("\n[5] Error recovery \u2014 validator.py handles malformed input gracefully")

    import tempfile

    print("\n  5a. Non-existent paths")
    result = validate_artifact("/tmp/nonexistent-artifact.json",
                               str(sop_schemas_dir / "sop-content.schema.json"))
    runner.check("validate_artifact missing artifact \u2192 ok=False", not result["ok"])
    runner.check("validate_artifact missing artifact \u2192 descriptive error",
                 any("Cannot read" in e for e in result.get("errors", [])),
                 f"errors: {result.get('errors')}")

    result = validate_artifact(str(sop_synthetic_dir / "sop-content-valid.json"),
                               "/tmp/nonexistent-schema.json")
    runner.check("validate_artifact missing schema \u2192 ok=False", not result["ok"])
    runner.check("validate_artifact missing schema \u2192 descriptive error",
                 any("Cannot read" in e for e in result.get("errors", [])),
                 f"errors: {result.get('errors')}")

    print("\n  5b. Invalid JSON content")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        tf.write("this is not json {{{ broken")
        bad_json_path = tf.name
    result = validate_artifact(bad_json_path,
                               str(sop_schemas_dir / "sop-content.schema.json"))
    os.unlink(bad_json_path)
    runner.check("validate_artifact invalid JSON \u2192 ok=False", not result["ok"])
    runner.check("validate_artifact invalid JSON \u2192 descriptive error",
                 any("Cannot read" in e or "JSON" in e for e in result.get("errors", [])),
                 f"errors: {result.get('errors')}")

    print("\n  5c. Missing required fields")
    content_schema = json.loads((sop_schemas_dir / "sop-content.schema.json").read_text())
    errs = validate_instance({"sop_code": "TEST"}, content_schema)
    runner.check("missing fields generates errors", len(errs) > 0)
    has_field_error = any("required" in e.lower() or "missing" in e.lower() for e in errs)
    runner.check("errors mention missing fields", has_field_error,
                 f"errors don't mention missing fields: {errs[:3]}")

    print("\n  5d. Wrong data types")
    wrong_type_doc = {
        "sop_code": 12345,
        "title": True,
        "process": "not a list",
        "evidence": "not a list",
        "confidence_score": "high",
        "need_review": "yes",
    }
    errs = validate_instance(wrong_type_doc, content_schema)
    runner.check("wrong types generates errors", len(errs) > 0)
    has_type_error = any("expected type" in e.lower() for e in errs)
    runner.check("errors mention type mismatches", has_type_error,
                 f"errors don't mention types: {errs[:3]}")

    print("\n  5e. Empty/minimal edge cases")
    errs = validate_instance({}, content_schema)
    runner.check("empty dict generates validation errors", len(errs) > 0,
                 "empty document should fail with required field errors")
    errs = validate_instance(None, content_schema)
    runner.check("null instance generates errors", len(errs) > 0)
    errs = validate_instance([], content_schema)
    runner.check("array instance (expected object) generates errors", len(errs) > 0)

    # ========================================================================
    # SLICE 6: Downstream Handoff — SOP ↔ XThinking
    # ========================================================================
    print("\n[6] Downstream handoff — sop-orchestrator → xthinking-orchestrator")

    XTHINK_DIR = get_xthinking_dir()
    runner.check("xthinking-orchestrator dir exists", XTHINK_DIR.is_dir())

    # 6a. SOP declares xthinking as downstream in skill.json
    xthink_downstream = sop_skill_json.get("integrations", {}).get("downstream", [])
    runner.check(
        "sop-orchestrator declares 'vibe-xthinking-orchestrator' as downstream",
        "vibe-xthinking-orchestrator" in xthink_downstream,
        f"downstream = {xthink_downstream}",
    )

    # 6b. Handoff schema exists on both sides
    sop_handoff_schema = SKILL_DIR / "schema" / "xthinking-handoff-brief.schema.json"
    xthink_handoff_schema = XTHINK_DIR / "schema" / "handoff-brief.schema.json"
    runner.check("sop xthinking-handoff-brief.schema.json exists",
                 sop_handoff_schema.is_file())
    runner.check("xthinking handoff-brief.schema.json exists",
                 xthink_handoff_schema.is_file())

    # 6c. Cross-validate: sop handoff schema can be parsed
    sop_schema = json.loads(sop_handoff_schema.read_text())
    runner.check("sop handoff schema is valid JSON", isinstance(sop_schema, dict))
    xthink_schema = json.loads(xthink_handoff_schema.read_text())
    runner.check("xthinking handoff schema is valid JSON", isinstance(xthink_schema, dict))

    # 6d. Evidence contract alignment: both schemas share the 3 required fields
    for field in ["evidence", "confidence_score", "need_review"]:
        runner.check(
            f"both schemas define '{field}'",
            field in sop_schema.get("required", [])
            and field in xthink_schema.get("required", []),
        )

    return runner.summary()


if __name__ == "__main__":
    sys.exit(main())
