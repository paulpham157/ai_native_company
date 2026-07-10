#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from test_helpers import get_skill_dir, check, summary as _summary, passed, failed


def main():
    global passed, failed
    print("=" * 60)
    print("TEST — detect_type: extension → artifact type mapping")
    print("=" * 60)

    from artifact_detector import detect_type

    KNOWN = {
        "/path/to/doc.md": "markdown",
        "/path/to/doc.markdown": "markdown",
        "/path/to/data.json": "json",
        "/path/to/config.yaml": "yaml",
        "/path/to/config.yml": "yaml",
    }

    UNKNOWN = {
        "/path/to/file.pdf": "unsupported",
        "/path/to/file.txt": "unsupported",
        "/path/to/file": "unsupported",
    }

    print("\n[1] Known extensions map to correct type")
    for path, expected in KNOWN.items():
        result = detect_type(path)
        check(
            f"detect_type('{Path(path).name}') == '{expected}'",
            result == expected,
            f"got '{result}'",
        )

    print("\n[2] Unknown extensions fall back to 'unsupported'")
    for path, expected in UNKNOWN.items():
        result = detect_type(path)
        check(
            f"detect_type('{Path(path).name}') == '{expected}'",
            result == expected,
            f"got '{result}'",
        )

    return _summary("detect-type", exit_on_fail=True)


if __name__ == "__main__":
    sys.exit(main())
