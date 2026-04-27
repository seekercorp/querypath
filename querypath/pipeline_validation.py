"""Pipeline integration for row-level validation."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from querypath.row_validator import apply_validation, parse_validation_spec


def run_pipeline_with_validation(
    rows: List[Dict[str, Any]],
    opts: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Apply validation rules from *opts* to *rows* and return the result.

    Expected opts shape::

        {
            "validate": {
                "rules": [
                    {"field": "name", "op": "not_null", "label": "name required"},
                    {"field": "age",  "op": "gte",      "value": 0},
                ],
                "mode": "flag",          # flag | drop | raise  (default: flag)
                "error_column": "_errors"  # optional, default _errors
            }
        }

    If no validation spec is present the rows are returned unchanged.
    """
    spec = parse_validation_spec(opts)
    if spec is None:
        return rows

    rules = spec.get("rules", [])
    if not rules:
        return rows

    mode = spec.get("mode", "flag")
    error_column = spec.get("error_column", "_errors")

    return apply_validation(rows, rules, mode=mode, error_column=error_column)


# ---------------------------------------------------------------------------
# Smoke test (run as script)
# ---------------------------------------------------------------------------

def _smoke_test() -> None:
    sample = [
        {"name": "Alice", "age": 30},
        {"name": None,   "age": 17},
        {"name": "Bob",  "age": None},
    ]
    opts = {
        "validate": {
            "rules": [
                {"field": "name", "op": "not_null", "label": "name required"},
                {"field": "age",  "op": "gte", "value": 18, "label": "age >= 18"},
            ],
            "mode": "flag",
        }
    }
    result = run_pipeline_with_validation(sample, opts)
    for row in result:
        print(row)

    print("\n--- drop mode ---")
    opts["validate"]["mode"] = "drop"  # type: ignore[index]
    result = run_pipeline_with_validation(sample, opts)
    for row in result:
        print(row)


if __name__ == "__main__":
    _smoke_test()
