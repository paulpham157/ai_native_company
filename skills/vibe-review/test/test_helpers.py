#!/usr/bin/env python3

import json
from pathlib import Path

try:
    import jsonschema
    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False


def get_skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def get_synthetic_dir() -> Path:
    return get_skill_dir() / "synthetic-data"


def load_fixture(name: str) -> dict:
    path = get_synthetic_dir() / f"{name}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Fixture not found: {path}")
    return json.loads(path.read_text())


def fixture_exists(name: str) -> bool:
    return (get_synthetic_dir() / f"{name}.json").is_file()


def load_schemas() -> dict[str, dict]:
    schemas = {}
    for sf in sorted((get_skill_dir() / "schema").glob("*.schema.json")):
        schemas[sf.name] = json.loads(sf.read_text())
    return schemas


def validate(schema: dict, instance: dict) -> list:
    if HAVE_JSONSCHEMA:
        return list(jsonschema.Draft7Validator(schema).iter_errors(instance))
    from validator import validate_instance
    return validate_instance(instance, schema)


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


def summary(label, exit_on_fail=True):
    print("\n" + "=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    if exit_on_fail:
        return 0 if failed == 0 else 1
    return failed
