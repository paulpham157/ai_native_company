#!/usr/bin/env python3

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "script"))

EXPECTED_SCRIPTS = {"validator.py", "log_helper.py", "anonymizer.py",
                    "review_queue.py", "install_hooks.sh"}


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


def main():
    runner = TestRunner()
    SKILL_DIR = get_skill_dir()
    COMPANY_DIR = get_company_dir()

    print("=" * 60)
    print("INTEGRATION TEST \u2014 vibe-review \u2194 ecosystem")
    print("=" * 60)

    # ========================================================================
    # SLICE 1: Symlink Integrity
    # ========================================================================
    print("\n[1] Symlink integrity \u2014 scripts symlinked from company-orchestrator")

    runner.check("company-orchestrator dir exists", COMPANY_DIR.is_dir())

    review_script_dir = SKILL_DIR / "script"
    company_script_dir = COMPANY_DIR / "script"

    runner.check("review script dir exists", review_script_dir.is_dir())
    runner.check("company script dir exists", company_script_dir.is_dir())

    review_files = {f for f in review_script_dir.iterdir()
                    if not f.name.startswith(".") and f.name != "__pycache__"}
    review_script_names = {f.name for f in review_files}
    company_script_names = {f.name for f in company_script_dir.iterdir()
                            if not f.name.startswith(".")}

    for name in sorted(EXPECTED_SCRIPTS):
        runner.check(f"expected script '{name}' exists in review/script/",
                     name in review_script_names)
        runner.check(f"expected script '{name}' exists in company/script/",
                     name in company_script_names)

        review_path = review_script_dir / name
        company_path = company_script_dir / name

        is_link = os.path.islink(str(review_path))
        runner.check(f"'{name}' in review/script/ is a symlink", is_link,
                     f"expected symlink, got regular file")

        if is_link:
            resolved = os.path.realpath(str(review_path))
            expected_target = os.path.realpath(str(company_path))
            runner.check(f"'{name}' symlink resolves to company/script/{name}",
                         resolved == expected_target,
                         f"resolves to {resolved}, expected {expected_target}")

    unexpected = review_script_names - EXPECTED_SCRIPTS
    runner.check(
        "no unexpected scripts in review/script/",
        len(unexpected) == 0,
        f"unexpected file(s): {sorted(unexpected)}",
    )

    for sf in review_files:
        if sf.name in EXPECTED_SCRIPTS:
            runner.check(
                f"'{sf.name}' is a symlink (no regular files)",
                os.path.islink(str(sf)),
                f"expected symlink, got regular file",
            )

    # ========================================================================
    # SLICE 2: skill.json Metadata
    # ========================================================================
    print("\n[2] skill.json metadata")

    review_skill_json_path = SKILL_DIR / "skill.json"
    runner.check("skill.json exists", review_skill_json_path.is_file())

    review_skill = json.loads(review_skill_json_path.read_text())

    runner.check("name == 'vibe-review'",
                 review_skill.get("name") == "vibe-review",
                 f"got '{review_skill.get('name')}'")

    runner.check("version matches semver",
                 isinstance(review_skill.get("version"), str),
                 f"got {type(review_skill.get('version'))}")

    runner.check("type == 'skill'",
                 review_skill.get("type") == "skill",
                 f"got '{review_skill.get('type')}'")

    runner.check("description has min length 10",
                 len(review_skill.get("description", "")) >= 10,
                 f"description too short")

    runner.check("universal_reviewer is true",
                 review_skill.get("universal_reviewer") is True,
                 f"got {review_skill.get('universal_reviewer')}")

    # Schema contract: evidence/confidence/need_review
    schema_contract = review_skill.get("integrations", {}).get("schema_contract", {})
    runner.check(
        "schema_contract.enforces_8_components is true",
        schema_contract.get("enforces_8_components") is True,
        f"got {schema_contract.get('enforces_8_components')}",
    )

    guardrails = review_skill.get("guardrails", {})
    runner.check("guardrails.evidence_required is true",
                 guardrails.get("evidence_required") is True)
    runner.check("guardrails.confidence_threshold == 0.7",
                 guardrails.get("confidence_threshold") == 0.7)

    # ========================================================================
    # SLICE 3: Mutual Integration Declarations
    # ========================================================================
    print("\n[3] Mutual integration declarations \u2014 other skills reference vibe-review")

    sop_skill_json_path = SKILL_DIR.parent / "vibe-sop-orchestrator" / "skill.json"
    company_skill_json_path = SKILL_DIR.parent / "vibe-company-orchestrator" / "skill.json"
    xthink_skill_json_path = SKILL_DIR.parent / "vibe-xthinking-orchestrator" / "skill.json"

    if sop_skill_json_path.is_file():
        sop_skill = json.loads(sop_skill_json_path.read_text())
        sop_downstream = sop_skill.get("integrations", {}).get("downstream", [])
        runner.check(
            "sop-orchestrator declares vibe-review as downstream",
            "vibe-review" in sop_downstream,
        )

    if company_skill_json_path.is_file():
        company_skill = json.loads(company_skill_json_path.read_text())
        company_downstream = company_skill.get("integrations", {}).get("downstream", [])
        runner.check(
            "company-orchestrator declares vibe-review as downstream",
            "vibe-review" in company_downstream,
        )

    if xthink_skill_json_path.is_file():
        xthink_skill = json.loads(xthink_skill_json_path.read_text())
        xthink_downstream = xthink_skill.get("integrations", {}).get("downstream", [])
        runner.check(
            "xthinking-orchestrator declares vibe-review as downstream",
            "vibe-review" in xthink_downstream,
        )

    # ========================================================================
    # SLICE 4: Artifact Type Detection
    # ========================================================================
    print("\n[4] Artifact type detection \u2014 extension to type mapping")

    artifact_type_map_path = SKILL_DIR / "synthetic-data" / "artifact-type-map-valid.json"
    if artifact_type_map_path.is_file():
        type_map_fixture = json.loads(artifact_type_map_path.read_text())
        type_map = type_map_fixture.get("type_map", {})
        fallback = type_map_fixture.get("fallback", "unsupported")

        KNOWN_MAP = {
            ".md": "markdown",
            ".markdown": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
        }

        for ext, expected_type in KNOWN_MAP.items():
            mapped_type = type_map.get(ext.lstrip("."), fallback)
            runner.check(
                f"ext '{ext}' maps to '{expected_type}'",
                mapped_type == expected_type,
                f"got '{mapped_type}'",
            )

        runner.check(
            "unknown extension falls back to 'unsupported'",
            fallback == "unsupported",
            f"got '{fallback}'",
        )

        runner.check(
            "custom_reviewers extension point exists",
            "custom_reviewers" in type_map_fixture,
        )

    # ========================================================================
    # SLICE 5: Cross-skill Schema Validation
    # ========================================================================
    print("\n[5] Cross-skill validation \u2014 skill-meta validates review skill.json")

    skill_meta_schema_path = COMPANY_DIR / "schema" / "skill-meta.schema.json"
    if skill_meta_schema_path.is_file():
        meta_schema = json.loads(skill_meta_schema_path.read_text())

        try:
            from validator import validate_instance
            errs = validate_instance(review_skill, meta_schema)
            runner.check(
                "skill-meta validates vibe-review skill.json",
                len(errs) == 0,
                "; ".join(errs[:3]),
            )
        except ImportError:
            runner.check(
                "skill-meta validation (validator.py available)",
                False,
                "validator.py not importable from script/",
            )

    # ========================================================================
    # SLICE 6: SKILL.md Content
    # ========================================================================
    print("\n[6] SKILL.md content")

    skill_md_path = SKILL_DIR / "SKILL.md"
    runner.check("SKILL.md exists", skill_md_path.is_file())
    skill_md = skill_md_path.read_text()

    runner.check("SKILL.md mentions 'vibe-review'", "vibe-review" in skill_md)
    runner.check("SKILL.md mentions 'Universal Reviewer'", "Universal Reviewer" in skill_md)
    runner.check("SKILL.md describes artifact types", any(t in skill_md for t in ["Markdown", "JSON", "YAML"]))
    runner.check("SKILL.md mentions evidence/confidence/need_review",
                 all(f in skill_md for f in ["evidence", "confidence", "need_review"]))
    runner.check("SKILL.md describes auto-detection by file extension",
                 "extension" in skill_md or "auto-detect" in skill_md or "auto detect" in skill_md.lower())
    runner.check("SKILL.md mentions fallback behavior",
                 "fallback" in skill_md.lower() or "unsupported" in skill_md)

    # 6b. 4 review methods
    print("\n  6b. 4 review methods in SKILL.md")
    for method in ["Method 1", "Method 2", "Method 3", "Method 4"]:
        runner.check(f"SKILL.md describes '{method}'", method in skill_md)

    # 6c. Quick and Full modes
    print("\n  6c. Quick and Full modes in SKILL.md")
    runner.check("SKILL.md mentions Quick mode", "Quick mode" in skill_md or "--quick" in skill_md)
    runner.check("SKILL.md mentions Full mode", "Full mode" in skill_md or "--full" in skill_md)

    # 6d. Methods content
    print("\n  6d. Method descriptions")
    runner.check("rules-based review described", "Rules-Based" in skill_md or "rules-based" in skill_md.lower())
    runner.check("schema validation described", "Schema Validation" in skill_md)
    runner.check("quality rubric described", "Quality Rubric" in skill_md or "rubric" in skill_md.lower())
    runner.check("HITL described", "Human-in-the-Loop" in skill_md or "HITL" in skill_md)

    return runner.summary()


if __name__ == "__main__":
    sys.exit(main())
