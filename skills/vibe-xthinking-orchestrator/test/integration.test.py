#!/usr/bin/env python3

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "script"))

EXPECTED_SCRIPTS = {"validator.py", "log_helper.py", "anonymizer.py",
                    "review_queue.py", "install_hooks.sh"}

XTHINK_SCHEMA_MAP = {
    "topic-analysis-valid": "topic-analysis.schema.json",
    "topic-analysis-minimal": "topic-analysis.schema.json",
    "problem-analysis-valid": "problem-analysis.schema.json",
    "problem-analysis-minimal": "problem-analysis.schema.json",
    "decision-analysis-valid": "decision-analysis.schema.json",
    "decision-analysis-minimal": "decision-analysis.schema.json",
    "evidence-tracking-valid": "evidence-tracking.schema.json",
    "evidence-tracking-minimal": "evidence-tracking.schema.json",
    "explicit-thinking-valid": "explicit-thinking.schema.json",
    "explicit-thinking-minimal": "explicit-thinking.schema.json",
}

XTHINK_INVALID_MAP = {
    "topic-analysis-invalid": "topic-analysis.schema.json",
    "problem-analysis-invalid": "problem-analysis.schema.json",
    "decision-analysis-invalid": "decision-analysis.schema.json",
}

EVIDENCE_FIELDS = {"evidence", "confidence_score", "need_review"}


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


def get_skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def get_company_dir() -> Path:
    return get_skill_dir().parent / "vibe-company-orchestrator"


def get_sop_dir() -> Path:
    return get_skill_dir().parent / "vibe-sop-orchestrator"


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
        f"unmapped fixtures: {unmapped}",
    )


def main():
    runner = TestRunner()
    SKILL_DIR = get_skill_dir()
    COMPANY_DIR = get_company_dir()
    SOP_DIR = get_sop_dir()

    print("=" * 60)
    print("INTEGRATION TEST \u2014 xthinking-orchestrator \u2194 ecosystem")
    print("=" * 60)

    # ========================================================================
    # SLICE 1: Symlink Integrity
    # ========================================================================
    print("\n[1] Symlink integrity \u2014 scripts symlinked from company-orchestrator")

    runner.check("company-orchestrator dir exists", COMPANY_DIR.is_dir())

    xthink_script_dir = SKILL_DIR / "script"
    company_script_dir = COMPANY_DIR / "script"

    runner.check("xthinking script dir exists", xthink_script_dir.is_dir())
    runner.check("company script dir exists", company_script_dir.is_dir())

    xthink_files = {f for f in xthink_script_dir.iterdir()
                    if not f.name.startswith(".") and f.name != "__pycache__"}
    xthink_script_names = {f.name for f in xthink_files}
    company_script_names = {f.name for f in company_script_dir.iterdir()
                            if not f.name.startswith(".")}

    for name in sorted(EXPECTED_SCRIPTS):
        runner.check(f"expected script '{name}' exists in xthinking/script/",
                     name in xthink_script_names)
        runner.check(f"expected script '{name}' exists in company/script/",
                     name in company_script_names)

        xthink_path = xthink_script_dir / name
        company_path = company_script_dir / name

        is_link = os.path.islink(str(xthink_path))
        runner.check(f"'{name}' in xthinking/script/ is a symlink", is_link,
                     f"expected symlink, got regular file")

        if is_link:
            resolved = os.path.realpath(str(xthink_path))
            expected_target = os.path.realpath(str(company_path))
            runner.check(f"'{name}' symlink resolves to company/script/{name}",
                         resolved == expected_target,
                         f"resolves to {resolved}, expected {expected_target}")

    unexpected = xthink_script_names - EXPECTED_SCRIPTS
    runner.check(
        "no unexpected scripts in xthinking/script/",
        len(unexpected) == 0,
        f"unexpected file(s): {sorted(unexpected)}",
    )

    for sf in xthink_files:
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

    xthink_skill_json = json.loads((SKILL_DIR / "skill.json").read_text())
    sop_skill_json = json.loads((SOP_DIR / "skill.json").read_text())
    company_skill_json = json.loads((COMPANY_DIR / "skill.json").read_text())

    runner.check("xthinking skill.json parses as valid JSON",
                 isinstance(xthink_skill_json, dict))

    xthink_upstream = xthink_skill_json.get("integrations", {}).get("upstream", [])
    sop_downstream = sop_skill_json.get("integrations", {}).get("downstream", [])
    company_downstream = company_skill_json.get("integrations", {}).get("downstream", [])

    runner.check(
        "xthinking declares 'vibe-company-orchestrator' as upstream",
        "vibe-company-orchestrator" in xthink_upstream,
    )
    runner.check(
        "xthinking declares 'vibe-sop-orchestrator' as upstream",
        "vibe-sop-orchestrator" in xthink_upstream,
    )
    runner.check(
        "sop-orchestrator declares 'vibe-xthinking-orchestrator' as downstream",
        "vibe-xthinking-orchestrator" in sop_downstream,
    )

    xthink_guardrails = xthink_skill_json.get("guardrails", {})
    guardrails_ok = (
        xthink_guardrails.get("evidence_required") is True
        and xthink_guardrails.get("confidence_threshold") == 0.7
        and xthink_guardrails.get("hooks_protected_paths") == ["template/", "archive/"]
    )
    runner.check("xthinking guardrails consistent (evidence_required, confidence_threshold=0.7, protected_paths)",
                 guardrails_ok)

    sop_guardrails = sop_skill_json.get("guardrails", {})
    company_guardrails = company_skill_json.get("guardrails", {})
    runner.check(
        "all 3 skills require evidence",
        xthink_guardrails.get("evidence_required") is True
        and sop_guardrails.get("evidence_required") is True
        and company_guardrails.get("evidence_required") is True,
    )
    runner.check(
        "all 3 skills have confidence_threshold == 0.7",
        xthink_guardrails.get("confidence_threshold") == 0.7
        and sop_guardrails.get("confidence_threshold") == 0.7
        and company_guardrails.get("confidence_threshold") == 0.7,
    )

    # ========================================================================
    # SLICE 3: Schema Cross-Validation
    # ========================================================================
    print("\n[3] Schema cross-validation \u2014 shared validator.py handles both skills")

    from validator import validate_artifact, validate_instance

    xthink_schemas_dir = SKILL_DIR / "schema"
    xthink_synthetic_dir = SKILL_DIR / "synthetic-data"

    print("\n  3a. Fixture-coverage guard")
    check_fixture_coverage(runner, xthink_synthetic_dir, XTHINK_SCHEMA_MAP,
                           XTHINK_INVALID_MAP, "xthinking")

    print("\n  3b. Xthinking \u2014 valid fixtures pass schema validation")
    for fixture_name, schema_name in sorted(XTHINK_SCHEMA_MAP.items()):
        fixture_path = xthink_synthetic_dir / f"{fixture_name}.json"
        schema_path = xthink_schemas_dir / schema_name
        if fixture_path.is_file() and schema_path.is_file():
            result = validate_artifact(str(fixture_path), str(schema_path))
            runner.check(f"xthink: {fixture_name}.json vs {schema_name}", result["ok"],
                         "; ".join(result["errors"][:3]))
        else:
            missing = [p for p, ok in [(fixture_name, fixture_path.is_file()),
                                       (schema_name, schema_path.is_file())] if not ok]
            runner.check(f"xthink: {fixture_name}.json vs {schema_name}", False,
                         f"missing: {missing}")

    print("\n  3c. Xthinking \u2014 invalid fixtures correctly rejected")
    for fixture_name, schema_name in sorted(XTHINK_INVALID_MAP.items()):
        fixture_path = xthink_synthetic_dir / f"{fixture_name}.json"
        schema_path = xthink_schemas_dir / schema_name
        if fixture_path.is_file() and schema_path.is_file():
            result = validate_artifact(str(fixture_path), str(schema_path))
            runner.check(f"xthink: {fixture_name}.json rejected", not result["ok"],
                         f"expected rejection, got ok=True")
        else:
            missing = [p for p, ok in [(fixture_name, fixture_path.is_file()),
                                       (schema_name, schema_path.is_file())] if not ok]
            runner.check(f"xthink: {fixture_name}.json rejected", False,
                         f"missing: {missing}")

    print("\n  3d. Cross-skill validation")
    skill_meta_schema_path = COMPANY_DIR / "schema" / "skill-meta.schema.json"
    if skill_meta_schema_path.is_file():
        meta_schema = json.loads(skill_meta_schema_path.read_text())
        xthink_skill = json.loads((SKILL_DIR / "skill.json").read_text())
        errs = validate_instance(xthink_skill, meta_schema)
        runner.check("skill-meta validates xthinking skill.json",
                     len(errs) == 0, "; ".join(errs[:3]))

        sop_skill = json.loads((SOP_DIR / "skill.json").read_text())
        errs = validate_instance(sop_skill, meta_schema)
        runner.check("skill-meta validates sop skill.json",
                     len(errs) == 0, "; ".join(errs[:3]))

        company_skill = json.loads((COMPANY_DIR / "skill.json").read_text())
        errs = validate_instance(company_skill, meta_schema)
        runner.check("skill-meta validates company skill.json",
                     len(errs) == 0, "; ".join(errs[:3]))
    else:
        runner.check("skill-meta.schema.json exists", False, "missing")

    # ========================================================================
    # SLICE 4: Evidence/Confidence/Need Review Contract
    # ========================================================================
    print("\n[4] Evidence contract \u2014 all valid/minimal fixtures emit "
          "evidence/confidence_score/need_review")

    def is_contract_fixture(path):
        return "invalid" not in path.stem and "-ignore" not in path.stem

    for fp in sorted(xthink_synthetic_dir.glob("*.json")):
        if not is_contract_fixture(fp):
            continue
        name = fp.name.replace(".json", "")
        doc = json.loads(fp.read_text())
        present = {f for f in EVIDENCE_FIELDS if f in doc}
        missing = EVIDENCE_FIELDS - present
        runner.check(
            f"xthink: {name} has all 3 required fields",
            len(missing) == 0,
            f"missing: {sorted(missing)}",
        )

    print("\n  4a. confidence_score in [0, 1]")
    for fp in sorted(xthink_synthetic_dir.glob("*.json")):
        if not is_contract_fixture(fp):
            continue
        name = fp.name
        doc = json.loads(fp.read_text())
        if "confidence_score" in doc:
            cs = doc["confidence_score"]
            runner.check(
                f"{name} confidence_score={cs} in [0,1]",
                isinstance(cs, (int, float)) and 0 <= cs <= 1,
                f"confidence_score={cs} out of range",
            )

    print("\n  4b. need_review is boolean")
    for fp in sorted(xthink_synthetic_dir.glob("*.json")):
        if not is_contract_fixture(fp):
            continue
        name = fp.name
        doc = json.loads(fp.read_text())
        if "need_review" in doc:
            nr = doc["need_review"]
            runner.check(
                f"{name} need_review={nr} is bool",
                isinstance(nr, bool),
                f"need_review={nr} is {type(nr).__name__}",
            )

    print("\n  4c. evidence is a list")
    for fp in sorted(xthink_synthetic_dir.glob("*.json")):
        if not is_contract_fixture(fp):
            continue
        name = fp.name
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

    print("\n  5a. Non-existent paths")
    result = validate_artifact("/tmp/nonexistent-artifact.json",
                               str(xthink_schemas_dir / "topic-analysis.schema.json"))
    runner.check("validate_artifact missing artifact \u2192 ok=False", not result["ok"])
    runner.check("validate_artifact missing artifact \u2192 descriptive error",
                 any("Cannot read" in e for e in result.get("errors", [])),
                 f"errors: {result.get('errors')}")

    result = validate_artifact(str(xthink_synthetic_dir / "topic-analysis-valid.json"),
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
                               str(xthink_schemas_dir / "topic-analysis.schema.json"))
    os.unlink(bad_json_path)
    runner.check("validate_artifact invalid JSON \u2192 ok=False", not result["ok"])
    runner.check("validate_artifact invalid JSON \u2192 descriptive error",
                 any("Cannot read" in e or "JSON" in e for e in result.get("errors", [])),
                 f"errors: {result.get('errors')}")

    print("\n  5c. Missing required fields")
    topic_schema = json.loads((xthink_schemas_dir / "topic-analysis.schema.json").read_text())
    errs = validate_instance({"analysis_id": "test"}, topic_schema)
    runner.check("missing fields generates errors", len(errs) > 0)
    has_field_error = any("required" in e.lower() or "missing" in e.lower() for e in errs)
    runner.check("errors mention missing fields", has_field_error,
                 f"errors don't mention missing fields: {errs[:3]}")

    print("\n  5d. Wrong data types")
    wrong_type_doc = {
        "analysis_id": 123,
        "topic": True,
        "mode": "invalid",
        "phases": "not-a-list",
        "evidence": "not-a-list",
        "confidence_score": "high",
        "need_review": "yes",
    }
    errs = validate_instance(wrong_type_doc, topic_schema)
    runner.check("wrong types generates errors", len(errs) > 0)
    has_type_error = any("expected type" in e.lower() for e in errs)
    runner.check("errors mention type mismatches", has_type_error,
                 f"errors don't mention types: {errs[:3]}")

    print("\n  5e. Empty/minimal edge cases")
    errs = validate_instance({}, topic_schema)
    runner.check("empty dict generates validation errors", len(errs) > 0)
    errs = validate_instance(None, topic_schema)
    runner.check("null instance generates errors", len(errs) > 0)
    errs = validate_instance([], topic_schema)
    runner.check("array instance (expected object) generates errors", len(errs) > 0)

    return runner.summary()


if __name__ == "__main__":
    sys.exit(main())
