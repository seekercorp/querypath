"""Tests for querypath/case_expr.py"""
import pytest
from querypath.case_expr import (
    evaluate_case,
    apply_case_column,
    parse_case_spec,
)


ROWS = [
    {"name": "Alice", "score": 92},
    {"name": "Bob", "score": 74},
    {"name": "Carol", "score": 55},
    {"name": "Dave", "score": 74},
]

GRADE_WHENS = [
    (("score", ">=", 90), "A"),
    (("score", ">=", 80), "B"),
    (("score", ">=", 70), "C"),
]


def test_evaluate_case_matches_first_when():
    row = {"score": 95}
    result = evaluate_case(row, GRADE_WHENS, else_value="F")
    assert result == "A"


def test_evaluate_case_matches_middle_when():
    row = {"score": 74}
    result = evaluate_case(row, GRADE_WHENS, else_value="F")
    assert result == "C"


def test_evaluate_case_falls_to_else():
    row = {"score": 50}
    result = evaluate_case(row, GRADE_WHENS, else_value="F")
    assert result == "F"


def test_evaluate_case_else_default_none():
    row = {"score": 10}
    result = evaluate_case(row, GRADE_WHENS)
    assert result is None


def test_evaluate_case_equality_op():
    whens = [(("status", "==", "active"), 1)]
    assert evaluate_case({"status": "active"}, whens, else_value=0) == 1
    assert evaluate_case({"status": "inactive"}, whens, else_value=0) == 0


def test_evaluate_case_not_equal_op():
    whens = [(("flag", "!=", None), "set")]
    assert evaluate_case({"flag": "yes"}, whens, else_value="unset") == "set"
    assert evaluate_case({"flag": None}, whens, else_value="unset") == "unset"


def test_evaluate_case_result_from_row_field():
    """THEN value can reference another field in the row."""
    whens = [(("score", ">=", 90), "name")]
    row = {"score": 95, "name": "Alice"}
    result = evaluate_case(row, whens, else_value="unknown")
    assert result == "Alice"


def test_apply_case_column_adds_alias():
    output = apply_case_column(ROWS, "grade", GRADE_WHENS, else_value="F")
    assert [r["grade"] for r in output] == ["A", "C", "F", "C"]


def test_apply_case_column_does_not_mutate():
    original = [{"score": 92}]
    apply_case_column(original, "grade", GRADE_WHENS, else_value="F")
    assert "grade" not in original[0]


def test_apply_case_column_empty_rows():
    assert apply_case_column([], "grade", GRADE_WHENS) == []


def test_parse_case_spec_present():
    spec = {"case": {"alias": "grade", "when_thens": [], "else": "F"}}
    result = parse_case_spec(spec)
    assert result == {"alias": "grade", "when_thens": [], "else": "F"}


def test_parse_case_spec_absent():
    assert parse_case_spec({"other": True}) is None


def test_evaluate_case_type_error_in_comparison_skips():
    """Non-comparable types should not raise; clause is skipped."""
    whens = [(("val", ">", "text"), "yes")]
    row = {"val": 10}
    result = evaluate_case(row, whens, else_value="no")
    assert result == "no"
