#!/usr/bin/env python3
"""
kb-validation.test.py — vibe-sop-orchestrator

Validates kb/ directory structure and content:
1. Required directories exist
2. Required KB files exist
3. Each markdown file has valid structure (heading, minimum content)
4. Template files follow expected format

Run:
    python3 test/kb-validation.test.py
"""

import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
KB_DIR = SKILL_DIR / "kb"
TEMPLATES_DIR = KB_DIR / "templates"

REQUIRED_FILES = [
    "mode-selection-rubric.md",
    "ipo-icom-framework.md",
    "sop-naming-conventions.md",
    "evidence-rubric.md",
    "quality-standards.md",
    "sop-quality-rubric.md",
    "sop-anti-patterns.md",
]

REQUIRED_INDUSTRY_TEMPLATES = [
    "tech-startup.md",
    "consulting.md",
    "ecommerce.md",
]

REQUIRED_TEMPLATES = [
    "sop-operational.md",
    "sop-documentation.md",
]

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
    print("KB VALIDATION TEST — vibe-sop-orchestrator")
    print("=" * 60)

    # [1] KB directory exists
    print("\n[1] KB directory structure")
    check("kb/ directory exists", KB_DIR.is_dir(), f"not found at {KB_DIR}")
    check("kb/templates/ directory exists", TEMPLATES_DIR.is_dir(), f"not found at {TEMPLATES_DIR}")

    # [2] Required KB files exist
    print("\n[2] Required KB files exist")
    for fname in REQUIRED_FILES:
        fpath = KB_DIR / fname
        check(f"kb/{fname} exists", fpath.is_file(), f"missing: {fpath}")

    # [3] Required industry template files exist
    print("\n[3] Required industry template files exist")
    industry_dir = KB_DIR / "industry-sop-templates"
    check("kb/industry-sop-templates/ directory exists", industry_dir.is_dir())
    for fname in REQUIRED_INDUSTRY_TEMPLATES:
        fpath = industry_dir / fname
        check(f"kb/industry-sop-templates/{fname} exists", fpath.is_file(), f"missing: {fpath}")

    # [4] Required template files exist
    print("\n[4] Required template files exist")
    for fname in REQUIRED_TEMPLATES:
        fpath = TEMPLATES_DIR / fname
        check(f"kb/templates/{fname} exists", fpath.is_file(), f"missing: {fpath}")

    # [4b] Industry templates have valid structure
    print("\n[4b] Industry template structure")
    for fname in REQUIRED_INDUSTRY_TEMPLATES:
        fpath = industry_dir / fname
        if not fpath.is_file():
            check(f"kb/industry-sop-templates/{fname} structure", False, "file missing")
            continue
        content = fpath.read_text()
        lines = content.strip().split("\n")
        has_h1 = any(line.startswith("# ") for line in lines)
        check(f"kb/industry-sop-templates/{fname}: has H1 heading", has_h1)
        check(f"kb/industry-sop-templates/{fname}: has >= 10 lines", len(lines) >= 10, f"got {len(lines)}")

    # [5] Each KB markdown file has valid structure
    print("\n[5] KB markdown files have valid structure")
    for fname in REQUIRED_FILES:
        fpath = KB_DIR / fname
        if not fpath.is_file():
            check(f"kb/{fname} structure valid", False, "file missing")
            continue
        content = fpath.read_text()
        lines = content.strip().split("\n")
        has_h1 = any(line.startswith("# ") for line in lines)
        min_lines = len(lines) >= 10
        has_content = len(content.strip()) >= 200
        check(
            f"kb/{fname}: has H1 heading",
            has_h1,
            "missing top-level heading (# Title)",
        )
        check(
            f"kb/{fname}: has >= 10 lines",
            min_lines,
            f"got {len(lines)} lines, expected >= 10",
        )
        check(
            f"kb/{fname}: has >= 200 chars",
            has_content,
            f"got {len(content.strip())} chars, expected >= 200",
        )

    # [6] Each template file has valid structure
    print("\n[6] Template files have valid structure")
    for fname in REQUIRED_TEMPLATES:
        fpath = TEMPLATES_DIR / fname
        if not fpath.is_file():
            check(f"kb/templates/{fname} structure valid", False, "file missing")
            continue
        content = fpath.read_text()
        lines = content.strip().split("\n")
        has_h1 = any(line.startswith("# ") for line in lines)
        has_placeholders = "{{" in content and "}}" in content
        check(
            f"kb/templates/{fname}: has H1 heading",
            has_h1,
            "missing top-level heading",
        )
        check(
            f"kb/templates/{fname}: has template placeholders {{...}}",
            has_placeholders,
            "no template placeholders found",
        )

    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
