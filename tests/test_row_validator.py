"""Tests for querypath.row_validator."""
import pytest
from querypath.row_validator import (
    _check_rule,
    validate_row,
    apply_validation,
    parse_validation_spec,
)


ROWS = [
    {"name": "Alice", "age": 30, "city": "NYC"},
    {"name": "Bob",   "age": None, "city": "LA"},
    {"name": None,   "age": 17,   "city": "NYC"},
]


# ---------------------------------------------------------------------------
# _check_rule
# ---------------------------------------------------------------------------

def test_not_null_pass():
    assert _check_rule({"x": 1}, {"field": "x", "op": "not_null"}) is True

def test_not_null_fail():
    assert _check_rule({"x": None}, {"field": "x", "op": "not_null"}) is False

def test_is_null_pass():
    assert _check_rule({"x": None}, {"field": "x", "op": "is_null"}) is True

def test_eq_pass():
    assert _check_rule({"x": "hi"}, {"field": "x", "op": "eq", "value": "hi"}) is True

def test_eq_fail():
    assert _check_rule({"x": "hi"}, {"field": "x", "op": "eq", "value": "bye"}) is False

def test_gt_pass():
    assert _check_rule({"age": 20}, {"field": "age", "op": "gt", "value": 18}) is True

def test_gt_fail():
    assert _check_rule({"age": 17}, {"field": "age", "op": "gt", "value": 18}) is False

def test_gt_none_returns_false():
    assert _check_rule({"age": None}, {"field": "age", "op": "gt", "value": 0}) is False

def test_lte_pass():
    assert _check_rule({"score": 100}, {"field": "score", "op": "lte", "value": 100}) is True

def test_in_pass():
    assert _check_rule({"role": "admin"}, {"field": "role", "op": "in", "value": ["admin", "user"]}) is True

def test_not_in_fail():
    assert _check_rule({"role": "admin"}, {"field": "role", "op": "not_in", "value": ["admin"]}) is False

def test_unknown_op_passes():
    assert _check_rule({"x": 1}, {"field": "x", "op": "mystery"}) is True


# ---------------------------------------------------------------------------
# validate_row
# ---------------------------------------------------------------------------

def test_validate_row_no_violations():
    rules = [{"field": "name", "op": "not_null"}]
    assert validate_row({"name": "Alice"}, rules) == []

def test_validate_row_one_violation():
    rules = [{"field": "name", "op": "not_null", "label": "name required"}]
    assert validate_row({"name": None}, rules) == ["name required"]

def test_validate_row_multiple_violations():
    rules = [
        {"field": "name", "op": "not_null"},
        {"field": "age", "op": "gt", "value": 18},
    ]
    violations = validate_row({"name": None, "age": 5}, rules)
    assert len(violations) == 2


# ---------------------------------------------------------------------------
# apply_validation — flag mode
# ---------------------------------------------------------------------------

def test_flag_mode_adds_error_column():
    rules = [{"field": "age", "op": "not_null"}]
    result = apply_validation(ROWS, rules, mode="flag")
    assert all("_errors" in r for r in result)

def test_flag_mode_valid_row_empty_errors():
    rules = [{"field": "age", "op": "not_null"}]
    result = apply_validation(ROWS, rules, mode="flag")
    assert result[0]["_errors"] == []

def test_flag_mode_invalid_row_has_errors():
    rules = [{"field": "age", "op": "not_null"}]
    result = apply_validation(ROWS, rules, mode="flag")
    assert len(result[1]["_errors"]) == 1

def test_flag_mode_custom_error_column():
    rules = [{"field": "name", "op": "not_null"}]
    result = apply_validation(ROWS, rules, mode="flag", error_column="issues")
    assert "issues" in result[0]


# ---------------------------------------------------------------------------
# apply_validation — drop mode
# ---------------------------------------------------------------------------

def test_drop_mode_removes_invalid():
    rules = [{"field": "name", "op": "not_null"}]
    result = apply_validation(ROWS, rules, mode="drop")
    assert all(r["name"] is not None for r in result)

def test_drop_mode_count():
    rules = [{"field": "age", "op": "not_null"}]
    result = apply_validation(ROWS, rules, mode="drop")
    assert len(result) == 2


# ---------------------------------------------------------------------------
# apply_validation — raise mode
# ---------------------------------------------------------------------------

def test_raise_mode_valid_rows_no_exception():
    rules = [{"field": "city", "op": "not_null"}]
    result = apply_validation(ROWS, rules, mode="raise")
    assert len(result) == 3

def test_raise_mode_raises_on_invalid():
    rules = [{"field": "name", "op": "not_null"}]
    with pytest.raises(ValueError, match="Row failed validation"):
        apply_validation(ROWS, rules, mode="raise")


# ---------------------------------------------------------------------------
# parse_validation_spec
# ---------------------------------------------------------------------------

def test_parse_returns_none_on_empty():
    assert parse_validation_spec(None) is None

def test_parse_returns_none_when_key_missing():
    assert parse_validation_spec({"other": 1}) is None

def test_parse_returns_spec():
    spec = {"rules": [{"field": "x", "op": "not_null"}], "mode": "drop"}
    opts = {"validate": spec}
    assert parse_validation_spec(opts) == spec
