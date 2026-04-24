"""Integration tests for pipeline_case.py"""
import pytest
from querypath.pipeline_case import extract_case_specs, run_pipeline_with_case


ROWS = [
    {"name": "Alice", "score": 92},
    {"name": "Bob", "score": 74},
    {"name": "Carol", "score": 55},
]


def _grade_spec(alias="grade"):
    return {
        "alias": alias,
        "when_thens": [
            {"field": "score", "op": ">=", "value": 90, "result": "A"},
            {"field": "score", "op": ">=", "value": 70, "result": "C"},
        ],
        "else": "F",
    }


def test_no_spec_returns_rows_unchanged():
    result = run_pipeline_with_case(ROWS, {})
    assert result == ROWS


def test_none_opts_returns_rows_unchanged():
    result = run_pipeline_with_case(ROWS, None)
    assert result == ROWS


def test_single_case_spec_adds_column():
    opts = {"case": _grade_spec()}
    result = run_pipeline_with_case(ROWS, opts)
    grades = [r["grade"] for r in result]
    assert grades == ["A", "C", "F"]


def test_multiple_cases_via_cases_key():
    opts = {
        "cases": [
            _grade_spec("grade"),
            {
                "alias": "pass_fail",
                "when_thens": [
                    {"field": "score", "op": ">=", "value": 70, "result": "pass"},
                ],
                "else": "fail",
            },
        ]
    }
    result = run_pipeline_with_case(ROWS, opts)
    assert [r["grade"] for r in result] == ["A", "C", "F"]
    assert [r["pass_fail"] for r in result] == ["pass", "pass", "fail"]


def test_case_and_cases_combined():
    """Single 'case' key and 'cases' list are both applied."""
    opts = {
        "case": _grade_spec("grade"),
        "cases": [
            {
                "alias": "label",
                "when_thens": [
                    {"field": "score", "op": ">=", "value": 90, "result": "top"}
                ],
                "else": "other",
            }
        ],
    }
    result = run_pipeline_with_case(ROWS, opts)
    assert "grade" in result[0]
    assert "label" in result[0]
    assert result[0]["label"] == "top"
    assert result[1]["label"] == "other"


def test_extract_case_specs_single():
    opts = {"case": _grade_spec()}
    specs = extract_case_specs(opts)
    assert len(specs) == 1
    assert specs[0]["alias"] == "grade"


def test_extract_case_specs_empty():
    assert extract_case_specs({}) == []


def test_pipeline_empty_rows():
    opts = {"case": _grade_spec()}
    assert run_pipeline_with_case([], opts) == []
