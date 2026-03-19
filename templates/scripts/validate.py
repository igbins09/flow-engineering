#!/usr/bin/env python3
"""
Flow Engineering — Generic Validation Template (Deterministic Layer)

This script validates LLM output against expected schema and constraints.
It is the critical gate between probabilistic and deterministic layers.

Usage:
  echo '{"decision": "approve", "confidence": 0.95}' | python validate.py
  python validate.py --input output.json
  python validate.py --input output.json --schema schema.json

Output:
  Validated JSON to stdout (passthrough on success).
  Error JSON to stderr with exit code 1 on failure.

Customize:
  1. Define REQUIRED_FIELDS for your schema
  2. Set VALID_ENUMS for constrained fields
  3. Add custom validation rules in validate()
"""

import argparse
import json
import sys
from pathlib import Path


# ── Schema Configuration ─────────────────────────────────────────────

REQUIRED_FIELDS = ["decision", "confidence", "items"]

VALID_ENUMS = {
    # "decision": ["approve", "reject", "escalate"],
    # "priority": ["low", "medium", "high", "critical"],
}

NUMERIC_RANGES = {
    "confidence": (0.0, 1.0),
    # "score": (0, 100),
}

ARRAY_FIELDS = {
    "items": {"min_length": 1},
    # "tags": {"min_length": 0},
}

# Required fields within each item in an array
ITEM_REQUIRED_FIELDS = {
    # "items": ["id", "classification", "action"],
}


# ── Validation Logic ─────────────────────────────────────────────────

def validate(data: dict) -> dict:
    """
    Validate LLM output against schema.

    Returns the data unchanged if valid.
    Raises ValueError with all validation errors if invalid.
    """
    errors = []

    # 1. Required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # 2. Enum validation
    for field, valid_values in VALID_ENUMS.items():
        if field in data and data[field] not in valid_values:
            errors.append(
                f"Invalid {field}: '{data[field]}'. Must be one of: {valid_values}"
            )

    # 3. Numeric range validation
    for field, (min_val, max_val) in NUMERIC_RANGES.items():
        if field in data:
            val = data[field]
            if not isinstance(val, (int, float)):
                errors.append(f"{field} must be numeric, got: {type(val).__name__}")
            elif not (min_val <= val <= max_val):
                errors.append(f"{field} = {val} is outside range [{min_val}, {max_val}]")

    # 4. Array validation
    for field, constraints in ARRAY_FIELDS.items():
        if field in data:
            val = data[field]
            if not isinstance(val, list):
                errors.append(f"{field} must be an array, got: {type(val).__name__}")
            else:
                min_len = constraints.get("min_length", 0)
                if len(val) < min_len:
                    errors.append(f"{field} has {len(val)} items, minimum is {min_len}")

                # Validate items within array
                if field in ITEM_REQUIRED_FIELDS:
                    for i, item in enumerate(val):
                        if not isinstance(item, dict):
                            errors.append(f"{field}[{i}] must be an object")
                            continue
                        for req_field in ITEM_REQUIRED_FIELDS[field]:
                            if req_field not in item:
                                errors.append(f"{field}[{i}] missing required field: {req_field}")

    # 5. Custom validation rules (add yours here)
    # Example:
    #   if data.get("confidence", 0) < 0.8 and data.get("decision") == "approve":
    #       errors.append("Cannot approve with confidence below 0.8")

    if errors:
        raise ValueError(f"Validation failed ({len(errors)} errors): {'; '.join(errors)}")

    return data


def validate_against_json_schema(data: dict, schema_path: str) -> dict:
    """Validate against a JSON Schema file (requires jsonschema package)."""
    try:
        import jsonschema
    except ImportError:
        print("Warning: jsonschema package not installed. Skipping JSON Schema validation.",
              file=sys.stderr)
        return data

    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    jsonschema.validate(instance=data, schema=schema)
    return data


# ── Main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Validate LLM output (D layer)")
    parser.add_argument("--input", help="Read from file instead of stdin")
    parser.add_argument("--schema", help="Path to JSON Schema file for additional validation")
    args = parser.parse_args()

    try:
        # Read input
        if args.input:
            raw = Path(args.input).read_text(encoding="utf-8")
        else:
            raw = sys.stdin.read()

        # Parse JSON
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from LLM: {e}")

        # Validate against built-in rules
        validated = validate(data)

        # Optional: validate against JSON Schema
        if args.schema:
            validated = validate_against_json_schema(validated, args.schema)

        # Output validated data
        print(json.dumps(validated, indent=2))

    except ValueError as e:
        print(json.dumps({
            "error": str(e),
            "step": "validate",
            "success": False,
        }), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "error": f"Unexpected error: {e}",
            "step": "validate",
            "success": False,
        }), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
