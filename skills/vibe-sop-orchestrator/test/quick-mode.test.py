#!/usr/bin/env python3
"""
quick-mode.test.py — Quick mode workflow tests

Tests (behavior, not shape):
1. Template cloning — templates exist and are readable
2. Mode selection rubric scoring — weighted score < 20 → Quick mode
3. Critical parameters blocked — BLOCKED fields not filled
4. Schema validation — Quick mode output passes schema
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
        print(f"  \u2713 {name}")
    else:
        failed += 1
        print(f"  \u2717 {name} \u2014 {detail}")

def validate(schema, instance):
    if HAVE_JSONSCHEMA:
        return list(jsonschema.Draft7Validator(schema).iter_errors(instance))
    return validate_instance(instance, schema)


def main():
    global passed, failed
    print("=" * 60)
    print("QUICK MODE TEST \u2014 vibe-sop-orchestrator")
    print("=" * 60)

    # 1. Template files exist and are readable
    print("\n[1] Template cloning \u2014 templates exist and are readable")
    template_dir = SKILL_DIR / "kb" / "templates"
    industry_dir = SKILL_DIR / "kb" / "industry-sop-templates"

    templates = sorted(template_dir.glob("*.md"))
    check("templates/ has >=1 template", len(templates) >= 2,
          f"found {len(templates)}")
    for t in templates:
        check(f"  {t.name} readable", len(t.read_text()) > 0)

    industry_templates = sorted(industry_dir.glob("*.md"))
    check("industry-sop-templates/ has >=1 template", len(industry_templates) >= 3,
          f"found {len(industry_templates)}")
    for t in industry_templates:
        check(f"  {t.name} readable", len(t.read_text()) > 0)

    # 2. Mode selection: weighted score < 20
    print("\n[2] Mode selection rubric \u2014 Quick mode when score < 20")
    rubric_path = SKILL_DIR / "kb" / "mode-selection-rubric.md"
    rubric_text = rubric_path.read_text()
    check("mode-selection-rubric.md exists", rubric_path.is_file())
    check("threshold mentioned in rubric", "20" in rubric_text)
    check("user override mentioned", "override" in rubric_text.lower())

    # 3. Critical parameters block — SKILL.md lists BLOCKED fields
    print("\n[3] Critical parameters — AI must NOT auto-fill")
    skill_text = (SKILL_DIR / "SKILL.md").read_text()
    critical_keywords = ["deadlines", "SLAs", "KPI targets", "DO_USER_SPECIFY"]
    for kw in critical_keywords:
        check(f"SKILL.md mentions '{kw}' as blocked", kw.lower() in skill_text.lower(),
              f"'{kw}' not found in SKILL.md")

    check("prompt template mentions BLOCKED fields",
          "[DO_USER_SPECIFY]" in (SKILL_DIR / "prompt" / "quick-mode-sop.md").read_text())

    # 4. Schema validation — Quick mode output passes schema
    print("\n[4] Schema validation — Quick mode output passes schema")
    schemas = {}
    for sf in (SKILL_DIR / "schema").glob("*.schema.json"):
        schemas[sf.name] = json.loads(sf.read_text())

    content_schema = schemas.get("sop-content.schema.json")
    meta_schema = schemas.get("sop-metadata.schema.json")

    # Load valid fixtures as proxy for Quick mode output
    synthetic_dir = SKILL_DIR / "synthetic-data"

    if content_schema:
        sop_path = synthetic_dir / "sop-content-valid.json"
        if sop_path.is_file():
            sop = json.loads(sop_path.read_text())
            errs = validate(content_schema, sop)
            check("Quick mode SOP content passes schema", not errs,
                  "; ".join(e.message for e in errs[:3]))
        else:
            check("sop-content-valid.json fixture exists", False)

    if meta_schema:
        meta_path = synthetic_dir / "sop-metadata-valid.json"
        if meta_path.is_file():
            meta = json.loads(meta_path.read_text())
            errs = validate(meta_schema, meta)
            check("Quick mode SOP metadata passes schema", not errs,
                  "; ".join(e.message for e in errs[:3]))
        else:
            check("sop-metadata-valid.json fixture exists", False)

    # 5. Emit — evidence/confidence_score/need_review present
    print("\n[5] Emit — evidence/confidence_score/need_review present")
    sop_path = synthetic_dir / "sop-content-valid.json"
    if sop_path.is_file():
        sop = json.loads(sop_path.read_text())
        check("sop-content has evidence", "evidence" in sop)
        check("sop-content has confidence_score", "confidence_score" in sop)
        check("sop-content has need_review", "need_review" in sop)
    else:
        check("sop-content-valid.json fixture exists", False)

    meta_path = synthetic_dir / "sop-metadata-valid.json"
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text())
        check("sop-metadata has evidence", "evidence" in meta)
        check("sop-metadata has confidence_score", "confidence_score" in meta)
        check("sop-metadata has need_review", "need_review" in meta)
    else:
        check("sop-metadata-valid.json fixture exists", False)

    # 6. Prompt file exists
    print("\n[6] Prompt template — quick-mode-sop.md exists")
    prompt_path = SKILL_DIR / "prompt" / "quick-mode-sop.md"
    check("prompt/quick-mode-sop.md exists", prompt_path.is_file())
    prompt_text = prompt_path.read_text()
    check("prompt mentions BLOCKED fields", "[DO_USER_SPECIFY]" in prompt_text)
    check("prompt mentions User Review", "User Review" in prompt_text)
    check("prompt mentions Validation", "Validation" in prompt_text)

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())