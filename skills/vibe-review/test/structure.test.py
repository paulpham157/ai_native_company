#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "script"))

from test_helpers import get_skill_dir, check, summary as _summary, passed, failed


def main():
    global passed, failed
    print("=" * 60)
    print("STRUCTURE TEST \u2014 vibe-review 8 components")
    print("=" * 60)

    SKILL_DIR = get_skill_dir()
    check("skill directory exists", SKILL_DIR.is_dir(), str(SKILL_DIR))

    expected_components = [
        "SKILL.md",
        "skill.json",
        "kb",
        "script",
        "prompt",
        "schema",
        "test",
        "synthetic-data",
    ]

    print("\n[1] 8-component structure")
    for comp in expected_components:
        path = SKILL_DIR / comp
        check(f"{comp} exists", path.exists(), str(path))

    return _summary("vibe-review structure", exit_on_fail=True)


if __name__ == "__main__":
    sys.exit(main())
