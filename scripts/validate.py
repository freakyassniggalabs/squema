#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver, validate, exceptions


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_examples(schema_path: Path, valid_dir: Path, invalid_dir: Path) -> int:
    schema = load_json(schema_path)
    base_uri = schema_path.parent.as_uri() + "/"
    resolver = RefResolver(base_uri=base_uri, referrer=schema)
    validator = Draft202012Validator(schema, resolver=resolver)

    failures = 0

    # Validate 'valid' examples must pass
    for example_file in sorted(valid_dir.glob("*.json")):
        data = load_json(example_file)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errors:
            print(f"FAIL valid: {example_file}")
            for err in errors:
                print(f"  -> {err.message}")
            failures += 1
        else:
            print(f"PASS valid: {example_file}")

    # Validate 'invalid' examples must fail
    for example_file in sorted(invalid_dir.glob("*.json")):
        data = load_json(example_file)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errors:
            print(f"PASS invalid: {example_file}")
        else:
            print(f"FAIL invalid (unexpectedly valid): {example_file}")
            failures += 1

    return failures


def main():
    parser = argparse.ArgumentParser(description="Validate circuit examples against schema")
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("schemas/circuit/v1.0.0/schema.json"),
        help="Path to schema.json",
    )
    parser.add_argument(
        "--valid",
        type=Path,
        default=Path("schemas/circuit/v1.0.0/examples/valid"),
        help="Path to valid examples directory",
    )
    parser.add_argument(
        "--invalid",
        type=Path,
        default=Path("schemas/circuit/v1.0.0/examples/invalid"),
        help="Path to invalid examples directory",
    )
    args = parser.parse_args()

    failures = validate_examples(args.schema, args.valid, args.invalid)
    if failures:
        print(f"\nValidation completed with {failures} failure(s).")
        sys.exit(1)
    else:
        print("\nAll validations passed.")


if __name__ == "__main__":
    main()


